def generate_report(root_event, chain, confidence=None, blast_radius=None):
    print("\nINCIDENT REPORT")
    print("=" * 40)

    # Root cause
    print("\nRoot Cause:")
    print(
        f"- {root_event['service']} failed at {root_event['timestamp']} "
        f"with event {root_event['event']}"
    )

    if confidence is not None:
        print(f"- confidence: {confidence:.2f}")

    # Propagation
    if len(chain) > 1:
        print("\nPropagation:")
        for e in chain[1:]:
            print(f"- {e['service']} | {e['event']}")
            if "first_seen" in e:
                print(f"  first_seen: {e['first_seen']}")
                print(f"  last_seen:  {e['last_seen']}")
                print(f"  occurrences: {e['occurrences']}")
                print(f"  duration: {e['duration']:.1f}s")
    else:
        print("\nPropagation:")
        print("- none detected")

    # Impact summary
    impacted = {
        e["service"]
        for e in chain
        if e["service"] != root_event["service"]
    }

    print("\nImpact Summary:")
    if impacted:
        print(f"- impacted services: {', '.join(sorted(impacted))}")
    else:
        print("- impacted services: none")

    if blast_radius is not None:
        print(f"- blast radius: {blast_radius}")
