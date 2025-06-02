#!/usr/bin/env python3
"""
Production pipeline for ABMS processing
"""

import argparse
import json
import subprocess
import time
from pathlib import Path

def validate_input(input_file):
    """Validate JSONL input file"""
    line_count = 0
    with open(input_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line)
                if 'text' not in data:
                    raise ValueError(f"Line {line_num}: Missing 'text' field")
                line_count += 1
            except json.JSONDecodeError as e:
                raise ValueError(f"Line {line_num}: Invalid JSON - {e}")
    return line_count

def process_batch(input_file, output_file, batch_size=1000):
    """Run ABMS batch encoding"""
    cmd = [
        'python', 'scripts/batch_encode.py',
        input_file, output_file,
        '--batch-size', str(batch_size)
    ]
    
    print(f"Processing {input_file}...")
    start_time = time.time()
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.2f} seconds")
    return True

def generate_summary(output_file):
    """Generate summary statistics"""
    aspects_stats = {}
    record_count = 0
    
    with open(output_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            record_count += 1
            
            aspects = data.get('aspects', {})
            for key, value in aspects.items():
                if key != 'data_hash' and isinstance(value, (int, float)):
                    if key not in aspects_stats:
                        aspects_stats[key] = []
                    aspects_stats[key].append(value)
    
    print(f"\nSummary for {record_count} records:")
    print("-" * 60)
    
    for aspect, values in sorted(aspects_stats.items()):
        avg = sum(values) / len(values)
        min_val = min(values)
        max_val = max(values)
        print(f"{aspect:35} avg: {avg:6.3f} (min: {min_val:6.3f}, max: {max_val:6.3f})")

def main():
    parser = argparse.ArgumentParser(description='ABMS Production Pipeline')
    parser.add_argument('input', help='Input JSONL file')
    parser.add_argument('output', help='Output JSONL file')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size')
    parser.add_argument('--validate-only', action='store_true', help='Only validate input')
    parser.add_argument('--summary', action='store_true', help='Generate summary stats')
    
    args = parser.parse_args()
    
    # Validate input
    try:
        line_count = validate_input(args.input)
        print(f"✓ Input validated: {line_count} records")
    except ValueError as e:
        print(f"✗ Validation failed: {e}")
        return 1
    
    if args.validate_only:
        return 0
    
    # Process
    if process_batch(args.input, args.output, args.batch_size):
        print(f"✓ Output written to {args.output}")
        
        if args.summary:
            generate_summary(args.output)
    else:
        return 1

if __name__ == '__main__':
    exit(main())
