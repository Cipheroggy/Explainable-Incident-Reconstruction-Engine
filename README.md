Explainable Incident Reconstruction Server

Offline tool that ingests structured logs and produces casual timeline 
explaining system failures using rule-based inferences

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

