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


def build_prompt(full_text: str) -> str:
    return f"""
You are a materials information extraction assistant.

TASK:
Extract alloy compositions mentioned in the paper.

Return STRICT JSON only.

We want compositions like:
- AZ31 = Mg + 3%Al + 1%Zn
- ZE10 = Mg + 1%Zn + 0.3%Ce

RULES:
- Output must be valid JSON only
- Use wt% or at% only if explicitly stated; otherwise keep unit as "percent"
- Use element symbols properly: Mg, Al, Zn, Ce
- If composition is written like "Mg+3 %Al+1 %Zn", parse it correctly

OUTPUT JSON schema:
{{
  "alloys": [
    {{
      "alloy_name": "AZ31",
      "composition": [
        {{"element": "Mg", "percent": null}},
        {{"element": "Al", "percent": 3}},
        {{"element": "Zn", "percent": 1}}
      ],
      "evidence": {{
        "snippet": "A well-known ... AZ31 (Mg+3 %Al+1 %Zn) ..."
      }}
    }}
  ]
}}

Paper text:
{full_text[:8000]}
""".strip()


def run_composition_agent(sections_json_path: str | Path) -> Dict[str, Any]:
    sections_json_path = Path(sections_json_path)

    if not sections_json_path.exists():
        raise FileNotFoundError(f"Missing sections JSON: {sections_json_path}")

    sections = json.loads(sections_json_path.read_text(encoding="utf-8"))

    # intro contains “Materials and Microstructures” in your case
    intro_text = sections.get("introduction", "") or ""
    full_text = intro_text

    prompt = build_prompt(full_text)

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Return only valid JSON. No markdown, no explanation."},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0}
    )

    content = strip_code_fences(response["message"]["content"])

    try:
        return json.loads(content)
    except Exception as e:
        raise ValueError(f"LLM returned non-JSON output.\nError: {e}\n\nOutput:\n{content}")
