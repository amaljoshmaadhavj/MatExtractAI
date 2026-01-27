import re


def normalize_units(text: str) -> str:
    if not text:
        return ""
    return (
        text
        .replace("Î¼", "μ")
        .replace("um", "μm")
    )


def value_in_evidence(value, snippet: str) -> bool:
    if value is None or not snippet:
        return False

    snippet = normalize_units(snippet)

    # Numeric values only
    if isinstance(value, (int, float)):
        number = int(value) if value == int(value) else value
        pattern = rf"{number}\s*(μm|MPa|%)"
        return re.search(pattern, snippet) is not None

    return False


def evaluate_record(record: dict) -> dict:
    evidence = normalize_units(
        record.get("evidence", {}).get("snippet", "")
    )

    checks = {}
    score = 0
    max_score = 0

    for key, value in record.items():
        if key in ["alloy", "variant", "material_form", "evidence"]:
            continue

        # Booleans → semantic
        if isinstance(value, bool):
            checks[key] = "semantic"
            continue

        # Qualitative strings → semantic
        if isinstance(value, str):
            checks[key] = "semantic"
            continue

        # Numeric values → must be verified
        if isinstance(value, (int, float)):
            max_score += 1
            if value_in_evidence(value, evidence):
                checks[key] = "verified"
                score += 1
            else:
                checks[key] = "unverified"
            continue

        # Missing numeric
        if value is None:
            max_score += 1
            checks[key] = "missing"

    confidence = (
        "high" if max_score > 0 and score / max_score >= 0.7 else
        "medium" if max_score > 0 and score / max_score >= 0.4 else
        "low"
    )

    return {
        "checks": checks,
        "confidence": confidence,
        "verified_ratio": round(score / max_score, 2) if max_score > 0 else 0.0
    }
