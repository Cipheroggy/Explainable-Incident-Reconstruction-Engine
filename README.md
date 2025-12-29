## Explainable Incident Reconstruction Engine

A graph-based incident analysis tool that reconstructs root causes and downstream failure propagation from distributed service logs.

This project focuses on causal reasoning, not ML hype. Given structured or semi-structured logs and a service dependency graph, it identifies what failed first, how the failure propagated, and which services were impacted, all offline.

## Log Schema (v1)

Each log entry MUST be a JSON object with the following fields:

- timestamp (string, ISO-8601, required)
- service (string, required)
- event (string, required)
- severity (INFO | WARN | ERROR, required)
- request_id (string or null)
- metadata (object)
    - dependency (string or null)
    - latency_ms (number or null)

## Why This Exists

Debugging distributed system failures is painful because:
  - Logs are fragmented across services
  - Errors cascade and mask the true root cause
  - Most student projects stop at log parsing or dashboards

This tool goes one step further:
  - It reconstructs causal chains
  - It explains why a failure happened
  - It outputs human-readable incident reports
No black-box ML. Just explicit reasoning you can inspect.

## What This Tool Can Detect

The engine is designed to detect dependency-driven incidents, such as:
  - Database outages → auth failures → API failures
  - Upstream service downtime → downstream unavailability
  - Repeated retry storms caused by a single root failure
  - Infrastructure or application-level failures when dependency relationships are known

Example incident detected:
```
DB_DOWN → DB_CONNECTION_FAILED → AUTH_SERVICE_UNAVAILABLE
```
## Core Capabilities
  - Normalize logs from multiple formats (JSON logs, Apache error/access logs)
  - Detect true root cause events
  - Reconstruct causal propagation timelines
  - Collapse noisy retries into meaningful events
  - Estimate blast radius and confidence score
  - Works fully offline (no cloud, no agents)

## Architecture
```
Raw Logs
   ↓
log_normalizer.py
   ↓
Normalized Events (JSON)
   ↓
analyze.py
   ├── Root Cause Detection
   ├── Incident Clustering
   ├── Causal Chain Reconstruction
   ├── Confidence + Blast Radius
   ↓
Incident Report
```
## Project Structure
```
incident-reconstruction/
├── analyze.py
├── log_normalizer.py
├── analyzer/
│   ├── anomaly.py
│   ├── causal.py
│   ├── incidents.py
│   ├── report.py
│   ├── confidence.py
│   ├── blast_radius.py
│   └── filter.py
├── config/
│   └── dependencies.json
├── logs/
└── examples/
```
## Dependency Graph

The system relies on an explicit service dependency graph.

Example (config/dependencies.json):
```
{
  "api": ["auth"],
  "auth": ["db"],
  "db": []
}
```
Meaning:
  - api depends on auth
  - auth depends on db
  - Root cause detection uses this graph to avoid blaming downstream services incorrectly.

## Step 1: Normalize Logs
Supported Inputs
  - JSON application logs
  - Apache access logs
  - Apache error logs
  - Mixed log sources in a single run

Command
```
python3 log_normalizer.py normalized.json logs/db_service.log logs/auth_service.log logs/api_service.log 
```
Output
A single normalized file:
```
[
  {
    "timestamp": "2025-12-28T17:12:34Z",
    "service": "db",
    "severity": "ERROR",
    "event": "DB_DOWN"
  }
]
```
This file is the only input required by the analysis engine.

Step 2: Analyze Incidents

Run the analysis engine on normalized logs:
```
python3 analyze.py normalized.json
```
## Example Output
```
Root Cause:
- db failed at 2025-12-28 17:12:34+00:00 with event DB_DOWN
- confidence: 0.72

Propagation:
- auth | DB_CONNECTION_FAILED
- api | AUTH_SERVICE_UNAVAILABLE

Impact Summary:
- impacted services: auth, api
- blast radius: MEDIUM
```

## Current Limitations
  - Requires accurate dependency graph
  - Time-window based propagation (configurable but heuristic)
  - Does not infer unknown dependencies automatically
  - Best suited for single dominant incident per time window
These are known and intentional trade-offs.

## Future Improvements (Open to Contributions)
  - Automatic dependency inference
  - Multi-root incident handling
  - Visualization of causal graphs
  - Streaming / near-real-time analysis
  - More log format adapters

Contributions, feedback, and ideas are welcome.
