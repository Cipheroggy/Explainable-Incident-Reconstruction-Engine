import json
import re
from datetime import datetime

# -------------------------
# CONFIG
# -------------------------
# Map processes / hosts / ports to service names
SERVICE_MAP = {
    # Syslog processes
    "sshd": "ssh",
    "nginx": "proxy",
    "postgres": "db",
    # Example app services
    "auth_service": "auth",
    "api_service": "api",
    # Add more as needed
}

# Map log levels or messages to severity
SEVERITY_MAP = {
    "error": "ERROR",
    "warn": "WARNING",
    "info": "INFO",
    # Add more mappings as needed
}

# -------------------------
# UTILITY FUNCTIONS
# -------------------------
def parse_iso(ts_str):
    """Normalize timestamps to ISO format."""
    try:
        # syslog may have formats like "Dec 26 22:40:01"
        dt = datetime.strptime(ts_str, "%b %d %H:%M:%S")
        # Year is missing, add current year
        dt = dt.replace(year=datetime.now().year)
    except ValueError:
        try:
            dt = datetime.fromisoformat(ts_str.replace("Z", ""))
        except ValueError:
            return None
    return dt.isoformat() + "Z"

def map_service(name):
    return SERVICE_MAP.get(name, name)

def map_severity(msg_or_level):
    msg_or_level = str(msg_or_level).lower()
    for key in SEVERITY_MAP:
        if key in msg_or_level:
            return SEVERITY_MAP[key]
    return "INFO"

# -------------------------
# PARSERS
# -------------------------
def parse_syslog_line(line):
    """
    Parse standard syslog line:
    e.g. "Dec 26 22:40:01 hostname process[pid]: message"
    """
    regex = r"^(?P<ts>\w+\s+\d+\s+\d+:\d+:\d+)\s+\S+\s+(?P<proc>[\w\-]+)(?:\[\d+\])?:\s+(?P<msg>.*)$"
    m = re.match(regex, line)
    if not m:
        return None
    ts = parse_iso(m.group("ts"))
    service = map_service(m.group("proc"))
    severity = map_severity(m.group("msg"))
    event = m.group("msg").strip()
    return {"timestamp": ts, "service": service, "severity": severity, "event": event}

def parse_app_log_line(line):
    """
    Parse JSON or simple text logs from applications.
    If JSON, expect keys: timestamp, service, severity, event
    """
    try:
        obj = json.loads(line)
        # Ensure required keys
        return {
            "timestamp": parse_iso(obj["timestamp"]),
            "service": map_service(obj["service"]),
            "severity": map_severity(obj["severity"]),
            "event": obj["event"]
        }
    except (json.JSONDecodeError, KeyError):
        # fallback: treat line as INFO
        ts = parse_iso(datetime.now().isoformat())
        return {"timestamp": ts, "service": "unknown_app", "severity": "INFO", "event": line.strip()}

def parse_db_log_line(line):
    """
    Minimal parser for DB logs (Postgres example)
    e.g. "2025-12-26 22:40:01.123 UTC [12345] ERROR:  connection failed"
    """
    regex = r"^(?P<ts>[\d\-\s:.]+)\s+\S+\s+\[\d+\]\s+(?P<level>\w+):\s+(?P<msg>.*)$"
    m = re.match(regex, line)
    if not m:
        return None
    ts = parse_iso(m.group("ts"))
    service = "db"
    severity = map_severity(m.group("level"))
    event = m.group("msg").strip()
    return {"timestamp": ts, "service": service, "severity": severity, "event": event}

def parse_proxy_log_line(line):
    """
    Minimal parser for proxy logs (Nginx combined log example)
    """
    # Example: 127.0.0.1 - - [26/Dec/2025:22:40:01 +0530] "GET /api HTTP/1.1" 502 123
    regex = r".*\[(?P<ts>[\d\/:]+)\s[+\-]\d+\]\s\".*\"\s(?P<status>\d{3})\s.*"
    m = re.match(regex, line)
    if not m:
        return None
    ts_str = m.group("ts")
    dt = datetime.strptime(ts_str, "%d/%b/%Y:%H:%M:%S")
    ts = dt.isoformat() + "Z"
    service = "proxy"
    status = int(m.group("status"))
    severity = "ERROR" if status >= 500 else "INFO"
    event = f"HTTP {status}"
    return {"timestamp": ts, "service": service, "severity": severity, "event": event}

# -------------------------
# MAIN NORMALIZER
# -------------------------
def normalize_logs(files):
    """
    files: list of dicts {type: "syslog"/"app"/"db"/"proxy", path: "file path"}
    returns: list of normalized logs (JSON array)
    """
    normalized = []

    for file_info in files:
        ftype = file_info["type"]
        path = file_info["path"]
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if ftype == "syslog":
                    parsed = parse_syslog_line(line)
                elif ftype == "app":
                    parsed = parse_app_log_line(line)
                elif ftype == "db":
                    parsed = parse_db_log_line(line)
                elif ftype == "proxy":
                    parsed = parse_proxy_log_line(line)
                else:
                    continue
                if parsed:
                    normalized.append(parsed)

    # Sort by timestamp
    normalized.sort(key=lambda x: x["timestamp"])
    return normalized

# -------------------------
# HELPER TO WRITE JSON FILE
# -------------------------
def write_normalized_json(normalized_logs, output_path):
    with open(output_path, "w") as f:
        json.dump(normalized_logs, f, indent=2)
