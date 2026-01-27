def aggregate_confidence(validation, cross_issues):
    """
    Adjust confidence based on cross-agent inconsistencies.
    """
    confidence = validation["confidence"]

    if cross_issues:
        if confidence == "high":
            return "medium"
        if confidence == "medium":
            return "low"

    return confidence
