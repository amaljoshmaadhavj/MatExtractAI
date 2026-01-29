import json
import re
from pathlib import Path
from typing import Dict, Any, List

import ollama

MODEL_NAME = "qwen2.5:3b"


def strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    if text.endswith("```"):
        text = text[:-3].strip()
    return text.strip()


def build_prompt(table_records: List[Dict[str, Any]], results_text: str) -> str:
    return f"""
You are a materials data extraction assistant.

TASK:
Extract mechanical properties for each alloy+variant and return STRICT JSON only.

RULES:
- Output must be VALID JSON only.
- Use Table 1 values as the ground truth.
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

Results text:
{results_text[:3000]}
""".strip()


def run_mechanical_properties_agent(
    pdf_name: str,
    output_dir: str | Path,
    sections: Dict[str, Any],
) -> Dict[str, Any]:

    output_dir = Path(output_dir)

    table1_path = output_dir / f"{pdf_name}_table1_clean.json"
    sections_path = output_dir / f"{pdf_name}_sections.json"
    out_path = output_dir / f"{pdf_name}_mech_agent.json"

    if not table1_path.exists():
        raise FileNotFoundError(f"Missing Table 1 JSON: {table1_path}")

    table_records = json.loads(table1_path.read_text(encoding="utf-8"))
    results_text = sections.get("results", "") or ""

    prompt = build_prompt(table_records, results_text)

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
        raise ValueError(f"Invalid JSON from LLM:\n{content}") from e

    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data
