#!/usr/bin/env python3
import json
import sys

if len(sys.argv) < 2:
    print("Usage: python show_aspects.py output.jsonl")
    sys.exit(1)

with open(sys.argv[1], 'r') as f:
    for line in f:
        data = json.loads(line)
        print(f"\nID: {data.get('id', 'unknown')}")
        print(f"Text: {data.get('text', '')[:100]}...")
        print("\nAspect Scores:")
        print("-" * 50)
        
        aspects = data.get('aspects', {})
        # Sort aspects for consistent display
        for key in sorted(aspects.keys()):
            if key != 'data_hash':
                value = aspects[key]
                if isinstance(value, float):
                    print(f"{key:40} {value:8.4f}")
                else:
                    print(f"{key:40} {value}")
