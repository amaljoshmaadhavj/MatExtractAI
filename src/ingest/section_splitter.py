import re
from typing import Dict, Any


SECTION_HEADERS = [
    "abstract",
    "introduction",
    "materials",
    "methods",
    "experimental",
    "results",
    "discussion",
    "conclusion",
    "references"
]


def split_sections(pdf_text: Dict[str, Any]) -> Dict[str, str]:
    full_text = "\n".join(p["text"] for p in pdf_text["pages"])
    lowered = full_text.lower()

    sections = {}
    for i, sec in enumerate(SECTION_HEADERS):
        start = lowered.find(sec)
        if start == -1:
            continue

        end = len(lowered)
        for next_sec in SECTION_HEADERS[i + 1:]:
            pos = lowered.find(next_sec, start + 10)
            if pos != -1:
                end = pos
                break

        sections[sec] = full_text[start:end].strip()

    return sections
