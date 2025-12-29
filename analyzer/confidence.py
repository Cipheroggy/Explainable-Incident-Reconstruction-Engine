def compute_root_confidence(root_event, chain):
    """
    Confidence is based on:
    - how many downstream services were impacted
    - how many total propagated events occurred
    """

    if not chain:
        return 0.1

    impacted_services = {
        e["service"]
        for e in chain
        if e["service"] != root_event["service"]
    }

    propagation_events = len(chain) - 1

    # Simple, explainable scoring
    confidence = (
        0.4 +
        0.3 * min(len(impacted_services) / 3, 1.0) +
        0.3 * min(propagation_events / 5, 1.0)
    )

    return round(confidence, 2)
