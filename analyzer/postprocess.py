from collections import OrderedDict

def collapse_retries(chain):
    """
    Merge repeated downstream failures (same service + event)
    into a single logical incident with counts.
    """
    collapsed = OrderedDict()

    for e in chain:
        key = (e["service"], e["event"])

        if key not in collapsed:
            collapsed[key] = {
                "service": e["service"],
                "event": e["event"],
                "role": e["role"],
                "first_timestamp": e["timestamp"],
                "last_timestamp": e["timestamp"],
                "count": 1
            }
        else:
            collapsed[key]["count"] += 1
            collapsed[key]["last_timestamp"] = e["timestamp"]

    return list(collapsed.values())
