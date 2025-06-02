#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import multiprocessing as mp
from functools import partial

# Import the processing function from your fixed script
from scripts.batch_encode_fixed import load_modules, process_text

def process_line(line, modules):
    """Process a single line"""
    try:
        data = json.loads(line.strip())
        if 'text' not in data:
            return None
        
        aspects = process_text(data['text'], modules)
        data['aspects'] = aspects
        return json.dumps(data)
    except:
        return None

def process_batch(lines, modules):
    """Process a batch of lines"""
    results = []
    for line in lines:
        result = process_line(line, modules)
        if result:
            results.append(result)
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    parser.add_argument('--workers', type=int, default=mp.cpu_count())
    parser.add_argument('--batch-size', type=int, default=100)
    args = parser.parse_args()
    
    print(f"🚀 Using {args.workers} workers on {mp.cpu_count()} available cores")
    
    # Load modules once in main process
    print("Loading modules...")
    modules = load_modules()
    
    # Read all lines
    with open(args.input_file, 'r') as f:
        lines = f.readlines()
    
    print(f"Processing {len(lines)} documents...")
    
    # Create batches
    batches = [lines[i:i+args.batch_size] for i in range(0, len(lines), args.batch_size)]
    
    # Process in parallel
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        # Submit all batches
        future_to_batch = {executor.submit(process_batch, batch, modules): batch 
                          for batch in batches}
        
        # Process results as they complete
        with open(args.output_file, 'w') as out:
            for future in tqdm(as_completed(future_to_batch), total=len(batches)):
                batch_results = future.result()
                for result in batch_results:
                    out.write(result + '\n')
    
    print(f"✅ Completed! Processed {len(lines)} documents")

if __name__ == '__main__':
    main()
