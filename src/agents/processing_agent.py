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


def build_prompt(text: str) -> str:
    return f"""
You are a materials data extraction assistant.

TASK:
Extract MATERIAL PROCESSING information from the paper.

Focus on:
- Product form: rolled sheet / extruded profile
- Condition: annealed condition, O-temper
- Heat treatment conditions: temperature (°C), time (h)
- Extrusion temperature
- Any casting/homogenization steps
- Thickness (mm) if present

RULES:
- Return STRICT JSON only.
- If temperature/time is not explicitly mentioned, use null.
- Keep numbers numeric, not strings.
- Evidence snippet should be a direct short phrase from the text.

OUTPUT JSON schema:
{{
  "processing_routes": [
    {{
      "material_form": "rolled sheet",
      "condition": "O-temper",
      "thickness_mm": 2,
      "steps": [
        {{"step": "annealed", "temperature_C": null, "time_h": null}},
        {{"step": "rolling", "temperature_C": null, "time_h": null}}
      ],
      "evidence": {{
        "snippet": "The two alloys are used in form of magnesium sheets in an annealed condition (O-temper) with a thickness of 2 mm."
      }}
    }},
    {{
      "material_form": "extruded profile",
      "condition": null,
      "thickness_mm": 1.7,
      "steps": [
        {{"step": "homogenization anneal", "temperature_C": 350, "time_h": 15}},
        {{"step": "extrusion", "temperature_C": 300, "time_h": null}}
      ],
      "evidence": {{
        "snippet": "Gravity cast slabs ... homogenization annealed for 15 h at 350 °C and extruded at 300 °C ..."
      }}
    }}
  ]
}}

Paper text:
{text[:4500]}
""".strip()


def run_processing_agent(sections_json_path: str | Path) -> Dict[str, Any]:
    sections_json_path = Path(sections_json_path)

    if not sections_json_path.exists():
        raise FileNotFoundError(f"Missing sections JSON: {sections_json_path}")

    sections = json.loads(sections_json_path.read_text(encoding="utf-8"))

    # Most processing info is in introduction in your case
    intro_text = sections.get("introduction", "") or ""

    prompt = build_prompt(intro_text)

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
        return json.loads(content)
    except Exception as e:
        raise ValueError(f"LLM returned non-JSON output.\nError: {e}\n\nOutput:\n{content}")