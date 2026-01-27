import re
from typing import Dict, List, Tuple


# ✅ Common section heading patterns in research papers
SECTION_ALIASES = {
    "abstract": ["abstract"],
    "introduction": ["introduction", "background"],
    "methods": [
        "materials and methods",
        "materials & methods",
        "methodology",
        "experimental",
        "experimental methods",
        "experimental procedure",
        "methods",
        "experiments",
    ],
    "results": [
        "results",
        "results and discussion",
        "results & discussion",
        "discussion",
    ],
    "conclusion": ["conclusion", "conclusions", "summary"],
    "references": ["references", "bibliography"],
}


def normalize_text(text: str) -> str:
    # remove repeated spaces
    text = re.sub(r"[ \t]+", " ", text)
    # remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def detect_section_heading(line: str) -> str | None:
    """
    Checks if a line matches any known section heading.
    Returns the canonical section name if found, else None.
    """
    clean = line.strip().lower()

    # remove numbering like "1. Introduction" or "2 INTRODUCTION"
    clean = re.sub(r"^\d+(\.\d+)*\s*", "", clean)
    clean = clean.replace(":", "").strip()

    for section, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if clean == alias:
                return section
    return None


def split_into_sections(full_text: str) -> Dict[str, str]:
    """
    Splits a paper text into major sections based on headings.
    Uses heuristic rules, works best for typical journal PDFs.
    """
    lines = full_text.splitlines()

    # Store tuples of (section_name, start_line_index)
    markers: List[Tuple[str, int]] = []

    for idx, line in enumerate(lines):
        if len(line.strip()) == 0:
            continue

        # headings are usually short
        if len(line.strip()) > 80:
            continue

        sec = detect_section_heading(line)
        if sec:
            markers.append((sec, idx))

    # If no markers found, fallback
    if not markers:
        return {
            "full_text": normalize_text(full_text)
        }

    # Sort by appearance order
    markers.sort(key=lambda x: x[1])

    # Build section chunks
    sections: Dict[str, str] = {}
    for i, (sec_name, start_idx) in enumerate(markers):
        end_idx = markers[i + 1][1] if i + 1 < len(markers) else len(lines)

        section_lines = lines[start_idx + 1:end_idx]  # skip heading line
        section_text = "\n".join(section_lines).strip()

        if sec_name in sections:
            # If section appears multiple times, append
            sections[sec_name] += "\n\n" + section_text
        else:
            sections[sec_name] = section_text

    # Clean up
    for k in list(sections.keys()):
        sections[k] = normalize_text(sections[k])

    return sections