from datetime import timedelta


def reconstruct_causal_chain(logs, graph, root_event, window_seconds=10):
    """
    Build a causal chain starting from a root event and
    following dependency propagation within a time window.
    """

    chain = []
    visited = set()

    def walk(event):
        service = event["service"]
        event_time = event["timestamp"]

        # Prevent infinite loops / duplicates
        key = (service, event_time, event["event"])
        if key in visited:
            return
        visited.add(key)

        # Assign role
        if event is root_event:
            role = "ROOT"
        else:
            role = "PROPAGATED"

        # Append the ACTUAL event (not a synthetic one)
        chain.append({
            "timestamp": event_time,
            "service": service,
            "event": event["event"],
            "role": role
        })

        # Time window for downstream effects
        window_end = event_time + timedelta(seconds=window_seconds)

        # Traverse dependency graph
        for downstream in graph.successors(service):
            for e in logs:
                if e["service"] != downstream:
                    continue

                e_time = e["timestamp"]

                if event_time < e_time <= window_end:
                    walk(e)

    # ---- START CAUSAL WALK ----
    walk(root_event)

    # Ensure chronological order
    chain.sort(key=lambda x: x["timestamp"])

    return chain
