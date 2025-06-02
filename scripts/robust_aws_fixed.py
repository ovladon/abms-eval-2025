#!/usr/bin/env python3
"""
Robust AWS-optimized ABMS batch encoder with dependency handling.

Gracefully handles missing dependencies and continues with available modules.
"""

import sys
import json
import pathlib
import argparse
from tqdm import tqdm
import traceback
import psutil
import hashlib
import gc
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Add src to Python path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

# Get system resources
TOTAL_RAM_GB = psutil.virtual_memory().total / (1024**3)
AVAILABLE_RAM_GB = psutil.virtual_memory().available / (1024**3)
CPU_COUNT = psutil.cpu_count()

print(f"🚀 AWS Resources:")
print(f"   Total RAM: {TOTAL_RAM_GB:.1f} GB")
print(f"   Available RAM: {AVAILABLE_RAM_GB:.1f} GB") 
print(f"   CPU Cores: {CPU_COUNT}")

# AWS-optimized chunk sizing
if AVAILABLE_RAM_GB > 100:
    DEFAULT_CHUNK_SIZE = 0  # No chunking
elif AVAILABLE_RAM_GB > 50:
    DEFAULT_CHUNK_SIZE = 100000
elif AVAILABLE_RAM_GB > 20:
    DEFAULT_CHUNK_SIZE = 50000
else:
    DEFAULT_CHUNK_SIZE = 10000

print(f"   Recommended chunk size: {'No chunking' if DEFAULT_CHUNK_SIZE == 0 else f'{DEFAULT_CHUNK_SIZE:,} chars'}")


def import_analysis_modules():
    """Dynamically import available analysis modules, skipping those with missing dependencies."""
    
    available_modules = []
    failed_modules = []
    
    # List of all module names from publisher_app.py
    module_names = [
        'ActionabilityAnalysis',
        'AudienceAppropriatenessAnalysis', 
        'CognitiveAnalysis',
        'ComplexityAnalysis',
        'ControversialityAnalysis',
        'CulturalContextAnalysis',
        'EmotionalPolarityAnalysis',
        'EthicalConsiderationsAnalysis',
        'FormalismAnalysis',
        'GenreAnalysis',
        'HumorAnalysis',
        'IntentionalityAnalysis',
        'InteractivityAnalysis',
        'LexicalDiversityAnalysis',
        'ModalityAnalysis',
        'MultimodalityAnalysis',
        'NarrativeStyleAnalysis',
        'NoveltyAnalysis',
        'ObjectivityAnalysis',
        'PersuasivenessAnalysis',
        'QuantitativeAnalysis',
        'QualitativeAnalysis',
        'ReadabilityAnalysis',
        'ReliabilityAnalysis',
        'SentimentAnalysis',
        'SocialOrientationAnalysis',
        'SpecificityAnalysis',
        'SpatialAnalysis',
        'SyntacticComplexityAnalysis',
        'TemporalAnalysis',
    ]
    
    for module_name in module_names:
        try:
            # Convert class name to module name (e.g., ActionabilityAnalysis -> actionability_analysis)
            snake_case = ''.join(['_' + c.lower() if c.isupper() and i > 0 else c.lower() 
                                 for i, c in enumerate(module_name)]).lstrip('_')
            
            module = __import__(f'abms.publisher.analysis_modules.{snake_case}', fromlist=[module_name])
            analysis_class = getattr(module, module_name)
            available_modules.append(analysis_class)
            
        except Exception as e:
            failed_modules.append((module_name, str(e)))
            continue
    
    print(f"📦 Module import results:")
    print(f"   ✅ Available: {len(available_modules)}/30 modules")
    if failed_modules:
        print(f"   ❌ Failed: {len(failed_modules)} modules")
        for name, error in failed_modules[:3]:  # Show first 3 failures
            print(f"      {name}: {error.split(':')[0] if ':' in error else error}")
        if len(failed_modules) > 3:
            print(f"      ... and {len(failed_modules) - 3} more")
    
    return available_modules


def import_metadata_generator():
    """Import metadata generator with fallback."""
    try:
        from publisher.aspect_based_metadata_generator import generate_aspect_based_metadata
        from Crypto.Random import get_random_bytes
        return generate_aspect_based_metadata, get_random_bytes
    except Exception as e:
        print(f"⚠️  Could not import metadata generator: {e}")
        print("   Continuing with raw analysis results only")
        return None, None


def aggregate_results(existing_results, new_results, categorical_counts):
    """Aggregate results across chunks (same logic as publisher_app.py)."""
    for key, value in new_results.items():
        if key in existing_results:
            if isinstance(value, (int, float)):
                existing_results[key] = (existing_results[key] + value) / 2
            elif isinstance(value, str):
                if key not in categorical_counts:
                    categorical_counts[key] = {}
                if value in categorical_counts[key]:
                    categorical_counts[key][value] += 1
                else:
                    categorical_counts[key][value] = 1
                most_frequent = max(categorical_counts[key], key=categorical_counts[key].get)
                existing_results[key] = most_frequent
        else:
            existing_results[key] = value
    return existing_results


def analyze_text_robust(text, chunk_size=0, analysis_modules=None):
    """
    Analyze text using available modules with error handling.
    """
    if not analysis_modules:
        print("❌ No analysis modules available")
        return {'analysis_results': {}, 'aspect_based_metadata': None, 'encryption_key': None}
    
    if chunk_size == 0:
        chunks = [text]
    else:
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    analysis_results = {}
    categorical_counts = {}
    successful_analyses = 0
    failed_analyses = 0
    
    # Process each chunk
    for chunk_idx, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
            
        # Run all available analysis modules on this chunk
        for module_class in analysis_modules:
            try:
                analysis_instance = module_class(chunk)
                result = analysis_instance.analyze()
                
                if result:  # Only aggregate if we got results
                    analysis_results = aggregate_results(analysis_results, result, categorical_counts)
                    successful_analyses += 1
                    
            except Exception as e:
                failed_analyses += 1
                # Continue with other modules - don't let one failure stop everything
                continue
    
    # Add data hash
    data_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    analysis_results["data_hash"] = data_hash
    
    # Try to generate metadata
    generate_metadata_func, get_random_bytes_func = import_metadata_generator()
    aspect_based_metadata = None
    encryption_key = None
    
    if generate_metadata_func and get_random_bytes_func:
        try:
            encryption_key = get_random_bytes_func(16)
            aspect_based_metadata = generate_metadata_func(analysis_results, encryption_key)
            encryption_key = encryption_key.hex()  # Convert to hex for JSON
        except Exception as e:
            print(f"⚠️  Metadata generation failed: {e}")
    
    print(f"   Analyses: {successful_analyses} successful, {failed_analyses} failed")
    
    return {
        'analysis_results': analysis_results,
        'aspect_based_metadata': aspect_based_metadata,
        'encryption_key': encryption_key
    }


def process_batch_robust(input_lines, chunk_size, analysis_modules, progress_interval=100):
    """Process all lines with robust error handling."""
    results = []
    total_successful = 0
    total_failed = 0
    
    for i, line in enumerate(tqdm(input_lines, desc="Processing documents")):
        try:
            obj = json.loads(line.strip())
            
            if 'text' not in obj or not obj['text'].strip():
                obj['aspects'] = {}
                obj['aspect_based_metadata'] = None
                obj['encryption_key'] = None
            else:
                # Run the ABMS analysis
                analysis_result = analyze_text_robust(obj['text'], chunk_size, analysis_modules)
                
                # Add results to object
                obj['aspects'] = analysis_result['analysis_results']
                obj['aspect_based_metadata'] = analysis_result['aspect_based_metadata']
                obj['encryption_key'] = analysis_result['encryption_key']
                
                total_successful += 1
            
            results.append(obj)
            
            # Memory management and progress reporting
            if i % progress_interval == 0 and i > 0:
                memory_usage = psutil.virtual_memory().percent
                print(f"   Processed {i:,} documents. Memory: {memory_usage:.1f}%")
                if memory_usage > 85:
                    gc.collect()
            
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON at line {i+1}")
            total_failed += 1
            continue
        except Exception as e:
            print(f"Warning: Error processing line {i+1}: {str(e)[:100]}...")
            total_failed += 1
            continue
    
    print(f"📊 Processing summary: {total_successful:,} successful, {total_failed:,} failed")
    return results


def main():
    parser = argparse.ArgumentParser(description="Robust AWS-optimized ABMS batch encoder")
    parser.add_argument("input", help="Input JSONL file")
    parser.add_argument("output", help="Output JSONL file")
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE,
                       help=f"Character chunk size (0=no chunking, default={DEFAULT_CHUNK_SIZE})")
    parser.add_argument("--progress-interval", type=int, default=100,
                       help="Show progress every N documents")
    
    args = parser.parse_args()
    
    print(f"🎯 Configuration:")
    print(f"   Input: {args.input}")
    print(f"   Output: {args.output}")
    print(f"   Chunk size: {'No chunking' if args.chunk_size == 0 else f'{args.chunk_size:,} chars'}")
    
    # Import available modules
    print("🔧 Loading analysis modules...")
    analysis_modules = import_analysis_modules()
    
    if not analysis_modules:
        print("❌ No analysis modules could be loaded. Please check dependencies.")
        sys.exit(1)
    
    # Create output directory
    pathlib.Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    # Read input data
    print(f"📖 Loading {args.input}...")
    with open(args.input, 'r') as f:
        input_lines = f.readlines()
    
    print(f"📊 Loaded {len(input_lines):,} documents")
    
    # Process all documents
    print("⚡ Starting analysis...")
    results = process_batch_robust(input_lines, args.chunk_size, analysis_modules, args.progress_interval)
    
    # Write results
    print(f"💾 Writing {len(results):,} results...")
    with open(args.output, 'w') as f:
        for obj in tqdm(results, desc="Writing output"):
            f.write(json.dumps(obj) + '\n')
    
    print(f"✅ Completed! Output written to {args.output}")
    
    # Show sample output
    if results:
        sample = results[0]
        aspects = sample.get('aspects', {})
        print(f"\n📈 Sample output:")
        print(f"   Text preview: {sample.get('text', '')[:100]}...")
        print(f"   Aspects found: {len(aspects)}")
        if aspects:
            print(f"   Sample aspects: {list(aspects.keys())[:5]}")
            # Show some sample values
            sample_values = {k: v for k, v in list(aspects.items())[:3]}
            print(f"   Sample values: {sample_values}")
        print(f"   Has metadata: {sample.get('aspect_based_metadata') is not None}")


if __name__ == "__main__":
    main()
