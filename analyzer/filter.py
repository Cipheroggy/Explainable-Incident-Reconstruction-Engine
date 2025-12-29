# analyzer/filter.py
def filter_logs(logs, min_severity="ERROR", ignore_events=None):
    """
    Filters logs based on severity and specific event names.

    Parameters:
    - logs: list of log dicts
    - min_severity: string, minimum severity to keep ("INFO" < "WARN" < "ERROR")
    - ignore_events: list of event names to ignore, e.g., ["heartbeat"]

    Returns:
    - Filtered list of logs
    """

    severity_rank = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3}

    if ignore_events is None:
        ignore_events = []

    filtered = [
        log
        for log in logs
        if severity_rank.get(log.get("severity", "INFO"), 0) >= severity_rank[min_severity]
        and log.get("event") not in ignore_events
    ]

    return filtered
