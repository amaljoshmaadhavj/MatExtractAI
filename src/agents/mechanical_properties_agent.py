import json
import re
from pathlib import Path
from typing import Dict, Any, List

import ollama


# ✅ Use smaller model to fit your RAM
MODEL_NAME = "qwen2.5:3b"


def strip_code_fences(text: str) -> str:
    """
    Removes markdown code fences like:
    ```json
    {...}
    ```
    """
    text = text.strip()

    # Remove opening fence: ```json or ```
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)

    # Remove closing fence: ```
    if text.endswith("```"):
        text = text[:-3].strip()

    return text.strip()


def build_prompt(table_records: List[Dict[str, Any]], results_text: str) -> str:
    return f"""
You are a materials data extraction assistant.

TASK:
Extract mechanical properties for each alloy+variant and return STRICT JSON only.

You are given:
1) Clean Table 1 records (high priority truth)
2) Paper Results text (secondary source for evidence snippets)

RULES:
- Output must be VALID JSON only (no markdown, no explanation).
- Use Table 1 values as the ground truth.
- Add a short evidence snippet for each record (can be from table header or results text).
- If any value is null, keep it null.
- Normalize variant capitalization exactly as:
  Sheet-RD, Sheet-TD, Extrusion-ED, Extrusion-TD

OUTPUT JSON schema:
{{
  "records": [
    {{
      "alloy": "AZ31",
      "variant": "Sheet-RD",
      "properties": {{
        "avg_grain_size_um": 15,
        "TYS_MPa": 170,
        "CYS_MPa": 72,
        "SD": 2.36,
        "UTS_MPa": 254,
        "fracture_strain_pct": 22.2
      }},
      "evidence": {{
        "source": "Table 1",
        "snippet": "Table 1 Mechanical properties of the rolled sheets and extrudates ..."
      }}
    }}
  ]
}}

Table records:
{json.dumps(table_records, indent=2)}

Results text (for evidence/support):
{results_text[:3500]}
""".strip()


def run_mechanical_properties_agent(
    table1_json_path: str | Path,
    sections_json_path: str | Path,
) -> Dict[str, Any]:
    table1_json_path = Path(table1_json_path)
    sections_json_path = Path(sections_json_path)

    if not table1_json_path.exists():
        raise FileNotFoundError(f"Missing Table 1 JSON: {table1_json_path}")

    if not sections_json_path.exists():
        raise FileNotFoundError(f"Missing sections JSON: {sections_json_path}")

    table_records = json.loads(table1_json_path.read_text(encoding="utf-8"))
    sections = json.loads(sections_json_path.read_text(encoding="utf-8"))

    results_text = sections.get("results", "") or ""

    prompt = build_prompt(table_records, results_text)

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Return only valid JSON. No markdown, no extra text."},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0}
    )

    content = response["message"]["content"].strip()

    # ✅ Fix: strip ```json fences if model returns them
    content = strip_code_fences(content)

    # ✅ Parse JSON safely
    try:
        data = json.loads(content)
    except Exception as e:
        raise ValueError(
            f"LLM returned non-JSON output.\nError: {e}\n\nOutput:\n{content}"
        )

    return data