import json
import re
from pathlib import Path
from typing import Dict, Any

import ollama

MODEL_NAME = "qwen2.5:3b"


def strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    if text.endswith("```"):
        text = text[:-3].strip()
    return text.strip()


def extract_grain_size_from_snippet(snippet: str):
    """
    Deterministically extract grain size in μm from evidence snippet.
    This avoids hallucination and keeps numeric extraction reliable.
    """
    if not snippet:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*μm", snippet)
    return float(match.group(1)) if match else None


def build_prompt(text: str) -> str:
    return f"""
You are a materials science data extraction agent.

TASK:
Extract MICROSTRUCTURE information for each alloy mentioned in the paper
(e.g., AZ31, ZE10).

Focus on:
- Average grain size (µm)
- Recrystallized or not
- Grain morphology (equi-axed, elongated, etc.)
- Texture description (strong basal texture, weak texture, etc.)
- Differences between rolled sheet and extruded material

RULES:
- Use ONLY information explicitly stated in the text.
- Do NOT infer or hallucinate.
- If a value is not explicitly stated, use null.
- Keep numerical values numeric.
- Return STRICT JSON only.
- Evidence snippet must be copied verbatim from the paper text.

OUTPUT JSON SCHEMA:
{{
  "microstructures": [
    {{
      "alloy": "AZ31",
      "material_form": "rolled sheet",
      "avg_grain_size_um": 15,
      "recrystallized": true,
      "grain_morphology": "equi-axed",
      "texture": "strong basal texture",
      "evidence": {{
        "snippet": "The sheets reveal a fully recrystallized microstructure resulting in a comparable average grain size of 15 μm."
      }}
    }}
  ]
}}

Paper text:
{text[:6000]}
""".strip()


def run_microstructure_agent(sections_json_path: str | Path) -> Dict[str, Any]:
    sections_json_path = Path(sections_json_path)

    if not sections_json_path.exists():
        raise FileNotFoundError(f"Missing sections JSON: {sections_json_path}")

    sections = json.loads(sections_json_path.read_text(encoding="utf-8"))

    # Combine all relevant sections for robust extraction
    source_text = (
        sections.get("materials and microstructures", "")
        + "\n"
        + sections.get("introduction", "")
        + "\n"
        + sections.get("results", "")
    )

    prompt = build_prompt(source_text)

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Return only valid JSON. No markdown."},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0}
    )

    content = strip_code_fences(response["message"]["content"])

    try:
        data = json.loads(content)
    except Exception as e:
        raise ValueError(
            f"LLM returned non-JSON output.\nError: {e}\n\nOutput:\n{content}"
        )

    # 🔒 Deterministic numeric correction (no hallucination)
    for entry in data.get("microstructures", []):
        if entry.get("avg_grain_size_um") is None:
            snippet = entry.get("evidence", {}).get("snippet", "")
            extracted = extract_grain_size_from_snippet(snippet)
            if extracted is not None:
                entry["avg_grain_size_um"] = extracted

    return data
