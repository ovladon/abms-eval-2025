#!/usr/bin/env python3
"""
Batch-encode JSONL files with ABMS (Aspect-Based Metadata System) aspects.

Usage:
    python scripts/batch_encode.py input.jsonl output.jsonl [--batch-size 1000]

Each input line must be a JSON object containing a "text" field.
Output adds "aspects" field with 30+ aspect scores.
"""

import sys
import json
import pathlib
import argparse
from tqdm import tqdm
import traceback
import importlib
import hashlib

# Add src to Python path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

# Import all analysis modules
analysis_modules = {}
module_names = [
    'actionability_analysis',
    'audience_appropriateness_analysis',
    'cognitive_analysis',
    'complexity_analysis',
    'controversiality_analysis',
    'cultural_context_analysis',
    'emotional_polarity_analysis',
    'ethical_considerations_analysis',
    'formalism_analysis',
    'genre_analysis',
    'humor_analysis',
    'intentionality_analysis',
    'interactivity_analysis',
    'lexical_diversity_analysis',
    'modality_analysis',
    'multimodality_analysis',
    'narrative_style_analysis',
    'novelty_analysis',
    'objectivity_analysis',
    'persuasiveness_analysis',
    'quantitative_analysis',
    'qualitative_analysis',
    'readability_analysis',
    'reliability_analysis',
    'sentiment_analysis',
    'social_orientation_analysis',
    'specificity_analysis',
    'spatial_analysis',
    'syntactic_complexity_analysis',
    'temporal_analysis'
]

print("Loading analysis modules...")
for module_name in module_names:
    try:
        # Import the module
        module = importlib.import_module(f'publisher.analysis_modules.{module_name}')
        
        # Get the class name (capitalize first letter of each word)
        class_name = ''.join(word.capitalize() for word in module_name.split('_'))
        
        # Get the class from the module
        if hasattr(module, class_name):
            analysis_modules[module_name] = getattr(module, class_name)
            print(f"✓ Loaded {module_name}")
        else:
            print(f"✗ Class {class_name} not found in {module_name}")
    except Exception as e:
        print(f"✗ Failed to load {module_name}: {e}")

def extract_aspects(text):
    """Extract all aspects from text using individual analysis modules."""
    results = {}
    
    # Calculate data hash
    text_bytes = text.encode('utf-8')
    results['data_hash'] = hashlib.sha256(text_bytes).hexdigest()
    
    # Run each analysis module
    for module_name, analyzer_class in analysis_modules.items():
        try:
            analyzer = analyzer_class(text)
            result = analyzer.analyze()
            results.update(result)
        except Exception as e:
            print(f"Error in {module_name}: {e}")
            # Set default value on error
            results[module_name.replace('_analysis', '_analysis')] = 0.0
    
    return results

def process_file(input_path, output_path, batch_size=1000):
    """Process JSONL file and add aspect analysis."""
    
    # Count total lines for progress bar
    total_lines = sum(1 for _ in open(input_path, 'r'))
    
    processed = 0
    failed = 0
    
    with open(input_path, 'r') as infile, \
         open(output_path, 'w') as outfile, \
         tqdm(total=total_lines, desc="Processing") as pbar:
        
        batch = []
        
        for line_num, line in enumerate(infile, 1):
            try:
                # Parse JSON
                data = json.loads(line.strip())
                
                if 'text' not in data:
                    print(f"Warning: Line {line_num} missing 'text' field, skipping")
                    failed += 1
                    pbar.update(1)
                    continue
                
                # Extract aspects
                aspects = extract_aspects(data['text'])
                
                # Add aspects to data
                data['aspects'] = aspects
                
                # Add to batch
                batch.append(data)
                processed += 1
                
                # Write batch if full
                if len(batch) >= batch_size:
                    for item in batch:
                        outfile.write(json.dumps(item) + '\n')
                    batch = []
                
            except json.JSONDecodeError as e:
                print(f"Error: Line {line_num} - Invalid JSON: {e}")
                failed += 1
            except Exception as e:
                print(f"Error: Line {line_num} - {e}")
                traceback.print_exc()
                failed += 1
            
            pbar.update(1)
        
        # Write remaining batch
        for item in batch:
            outfile.write(json.dumps(item) + '\n')
    
    print(f"\nProcessing complete!")
    print(f"Processed: {processed} records")
    print(f"Failed: {failed} records")
    print(f"Output written to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Batch encode texts with ABMS aspects')
    parser.add_argument('input_file', help='Input JSONL file')
    parser.add_argument('output_file', help='Output JSONL file')
    parser.add_argument('--batch-size', type=int, default=1000,
                        help='Batch size for writing (default: 1000)')
    
    args = parser.parse_args()
    
    # Validate input file exists
    input_path = pathlib.Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    # Process the file
    process_file(args.input_file, args.output_file, args.batch_size)

if __name__ == '__main__':
    main()
