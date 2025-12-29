import json
import sys
from datetime import datetime

from analyzer.graph import load_dependency_graph
from analyzer.causal import reconstruct_causal_chain
from analyzer.report import generate_report
from analyzer.validate import validate_logs
from analyzer.anomaly import detect_root_causes
from analyzer.incidents import cluster_incidents, choose_dominant_root
from analyzer.filter import filter_logs
from analyzer.postprocess import collapse_retries

# 🔥 UPGRADE IMPORTS 🔥
from analyzer.confidence import compute_root_confidence
from analyzer.blast_radius import compute_blast_radius


# -------------------------
# TIMESTAMP PARSER
# -------------------------
def parse_timestamp(ts):
    if isinstance(ts, datetime):
        return ts
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


# -------------------------
# MAIN
# -------------------------
def main():
    if len(sys.argv) != 2:
        print("Usage: python3 analyze.py <normalized_logs.json>")
        sys.exit(1)

    input_file = sys.argv[1]

    # 1️⃣ Load normalized logs
    with open(input_file) as f:
        logs = json.load(f)

    # 2️⃣ Parse timestamps
    for e in logs:
        e["timestamp"] = parse_timestamp(e["timestamp"])

    print(f"Loaded {len(logs)} normalized log events")

    # 3️⃣ Filter noise
    logs = filter_logs(
        logs,
        min_severity="ERROR",
        ignore_events=["heartbeat"]
    )
    print(f"{len(logs)} events remain after filtering noise")

    # 4️⃣ Validate & sort
    logs = validate_logs(logs)
    logs.sort(key=lambda x: x["timestamp"])

    # 5️⃣ Load dependency graph
    graph = load_dependency_graph("config/dependencies.json")

    # 6️⃣ Detect root causes & cluster incidents
    root_candidates = detect_root_causes(logs, graph)
    incidents = cluster_incidents(root_candidates)

    # 7️⃣ Process each incident
    for idx, incident_roots in enumerate(incidents, start=1):
        print(f"\nINCIDENT #{idx}")
        print("=" * 50)

        root_event = choose_dominant_root(incident_roots, graph)

        raw_chain = reconstruct_causal_chain(
            logs,
            graph,
            root_event
        )

        collapsed_chain = collapse_retries(raw_chain)

        # 🔥 UPGRADE 1: CONFIDENCE SCORE
        confidence = compute_root_confidence(
            root_event,
            collapsed_chain
        )

        # 🔥 UPGRADE 3: BLAST RADIUS
        blast_radius = compute_blast_radius(
            root_event=root_event,
            chain=collapsed_chain
        )

        generate_report(
            root_event,
            collapsed_chain,
            confidence=confidence,
            blast_radius=blast_radius
        )


if __name__ == "__main__":
    main()
