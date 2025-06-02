#!/usr/bin/env python3
"""
Verify that batch encoding produces consistent results with the Streamlit UI.
"""

import sys
import json
import pathlib
from tqdm import tqdm
import numpy as np

# Add src to path  
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

def extract_aspects_ui_style(text):
    """Extract aspects using the same method as the UI."""
    try:
        # This should match exactly what the Streamlit app does
        import publisher.publisher_app as app
        from publisher.aspect_based_metadata_generator import AspectBasedMetadataGenerator
        
        generator = AspectBasedMetadataGenerator()
        return generator.generate_metadata(text)
        
    except Exception as e:
        print(f"Error in UI-style extraction: {e}")
        return {}


def compare_aspect_dicts(dict1, dict2, tolerance=1e-6):
    """Compare two aspect dictionaries and report differences."""
    all_keys = set(dict1.keys()) | set(dict2.keys())
    differences = {}
    
    for key in all_keys:
        val1 = dict1.get(key, None)
        val2 = dict2.get(key, None)
        
        if val1 is None:
            differences[key] = f"Missing in dict1, dict2={val2}"
        elif val2 is None:
            differences[key] = f"Missing in dict2, dict1={val1}"
        elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            if abs(val1 - val2) > tolerance:
                differences[key] = f"Numeric diff: {val1} vs {val2} (diff={abs(val1-val2)})"
        elif val1 != val2:
            differences[key] = f"Value diff: {val1} vs {val2}"
            
    return differences


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/verify_consistency.py batch_output.jsonl")
        sys.exit(1)
        
    batch_file = sys.argv[1]
    
    print("Loading batch results...")
    with open(batch_file, 'r') as f:
        batch_results = [json.loads(line) for line in f]
    
    # Test on first 10 samples
    print("Testing consistency on first 10 samples...")
    
    total_samples = 0
    total_differences = 0
    
    for i, batch_result in enumerate(batch_results[:10]):
        if 'text' not in batch_result or 'aspects' not in batch_result:
            continue
            
        text = batch_result['text']
        batch_aspects = batch_result['aspects']
        
        print(f"\nSample {i+1}:")
        print(f"Text: {text[:100]}...")
        
        # Generate aspects using UI method
        ui_aspects = extract_aspects_ui_style(text)
        
        # Compare
        differences = compare_aspect_dicts(batch_aspects, ui_aspects)
        
        if differences:
            print(f"❌ Found {len(differences)} differences:")
            for key, diff in list(differences.items())[:5]:  # Show first 5
                print(f"  {key}: {diff}")
            if len(differences) > 5:
                print(f"  ... and {len(differences) - 5} more")
            total_differences += len(differences)
        else:
            print("✅ Perfect match!")
            
        total_samples += 1
    
    print(f"\n=== SUMMARY ===")
    print(f"Tested {total_samples} samples")
    print(f"Total differences found: {total_differences}")
    
    if total_differences == 0:
        print("🎉 Batch and UI methods are perfectly consistent!")
    else:
        print(f"⚠️  Average {total_differences/total_samples:.1f} differences per sample")
        print("This might be due to randomness or different initialization")


if __name__ == "__main__":
    main()
