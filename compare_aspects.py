#!/usr/bin/env python3
import json
import sys

aspects_to_compare = [
    'actionability_analysis',
    'social_orientation_analysis', 
    'specificity_analysis',
    'controversiality_analysis',
    'lexical_diversity_analysis',
    'quantitative_analysis'
]

print(f"{'Text Sample':<50} {'Aspect':<30} {'Value':<10}")
print("-" * 90)

with open(sys.argv[1], 'r') as f:
    for line in f:
        data = json.loads(line)
        text_preview = data.get('text', '')[:47] + "..."
        aspects = data.get('aspects', {})
        
        for aspect in aspects_to_compare:
            if aspect in aspects:
                value = aspects[aspect]
                if isinstance(value, float):
                    print(f"{text_preview:<50} {aspect:<30} {value:8.4f}")
                else:
                    print(f"{text_preview:<50} {aspect:<30} {value}")
        print()
