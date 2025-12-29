SEVERITY_WEIGHT = {
    "INFO": 0,
    "WARN": 1,
    "ERROR": 2,
}

def score_event(event, dependency_graph):
    score = 0

    # Severity matters
    score += SEVERITY_WEIGHT.get(event["severity"], 0)

    # Impact matters (how many services depend on it)
    service = event["service"]
    if service in dependency_graph:
        score += len(list(dependency_graph.successors(service)))

    return score

def detect_root_candidates(logs, dependency_graph, min_score=2):
    candidates = []

    for event in logs:
        score = score_event(event, dependency_graph)
        if score >= min_score and is_true_root(event, logs, dependency_graph):
            candidates.append((score, event))

    candidates.sort(key=lambda x: x[1]["timestamp"])
    return [e for _, e in candidates]


# Sort by time (earliest first)
def detect_root_causes(logs, graph):
    """
    Return all ERROR events that are either:
    1. Not caused by upstream dependencies (no upstream failure logged)
    2. Upstream services not present in logs (inferred root)
    """
    roots = []

    # Collect services that had errors
    services_with_errors = {e["service"] for e in logs if e["severity"] == "ERROR"}

    for event in logs:
        if event["severity"] != "ERROR":
            continue

        service = event["service"]

        try:
            upstream = list(graph.predecessors(service))
        except KeyError:
            # Service not in graph; treat as root
            roots.append(event)
            continue

        # If no upstream failed, consider this event a root
        if not any(dep in services_with_errors for dep in upstream):
            roots.append(event)

    return roots


def is_true_root(event, logs, dependency_graph):
    service = event["service"]
    event_time = event["timestamp"]

    # Any upstream service that failed before this?
    for upstream in dependency_graph.predecessors(service):
        for log in logs:
            if (
                log["service"] == upstream
                and log["severity"] == "ERROR"
                and log["timestamp"] < event_time
            ):
                return False

    return True
