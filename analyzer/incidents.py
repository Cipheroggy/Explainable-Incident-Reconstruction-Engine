from datetime import timedelta


def cluster_incidents(root_events, max_gap_seconds=10):
    incidents = []

    for event in sorted(root_events, key=lambda x: x["timestamp"]):
        placed = False

        for incident in incidents:
            last = incident[-1]

            if (
                event["service"] == last["service"]
                and event["event"] == last["event"]
                and event["timestamp"] - last["timestamp"] <= timedelta(seconds=max_gap_seconds)
            ):
                incident.append(event)
                placed = True
                break

        if not placed:
            incidents.append([event])

    return incidents


# Choose the dominant root cause for an incident
def choose_dominant_root(incident_roots, graph):
    def score(event):
        service = event["service"]
        # Higher downstream impact = higher score
        return len(list(graph.successors(service)))

    return max(incident_roots, key=score)
