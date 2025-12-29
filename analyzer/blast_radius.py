from datetime import datetime


def compute_blast_radius(root_event, chain):
    """
    Blast radius is based on:
    - total duration of impact
    - number of downstream services affected
    """

    times = []

    # Root event time
    times.append(root_event["timestamp"])

    # Propagation windows
    for e in chain:
        if "first_seen" in e:
            times.append(e["first_seen"])
        if "last_seen" in e:
            times.append(e["last_seen"])

    if not times:
        return "LOW"

    start = min(times)
    end = max(times)
    duration = (end - start).total_seconds()

    impacted_services = {
        e["service"]
        for e in chain
        if e["service"] != root_event["service"]
    }

    # Simple, explainable classification
    if duration > 30 or len(impacted_services) >= 3:
        return "HIGH"
    elif duration > 10 or len(impacted_services) >= 1:
        return "MEDIUM"
    else:
        return "LOW"
