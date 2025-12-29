REQUIRED_FIELDS = {"timestamp", "service", "event", "level"}

REQUIRED_FIELDS = {"timestamp", "service", "event", "severity"}

def validate_logs(logs):
    validated = []

    for i, log in enumerate(logs):
        if not isinstance(log, dict):
            raise ValueError(f"Log {i} is not an object")

        missing = REQUIRED_FIELDS - log.keys()
        if missing:
            raise ValueError(f"Log {i} missing fields: {missing}")

        if log["severity"] not in {"INFO", "WARN", "ERROR"}:
            raise ValueError(
                f"Log {i} has invalid severity: {log['severity']}"
            )

        validated.append(log)

    return validated

