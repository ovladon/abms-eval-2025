#!/usr/bin/env python3
"""
AWS-optimized ABMS batch encoder - eliminates laptop constraints!

Based on analysis of publisher_app.py:
- Original: 1000-char chunks + resource throttling for laptops
- AWS optimized: Large chunks or no chunking + full resource utilization

Usage:
    python scripts/aws_optimized_batch_encode.py input.jsonl output.jsonl [--chunk-size 0]
    
    --chunk-size 0 = no chunking (process entire documents at once)
    --chunk-size N = use N-character chunks (default: auto-detect based on RAM)
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
from Crypto.Random import get_random_bytes

# Add src to Python path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

# Import all 30 analysis modules (exactly like publisher_app.py)
from publisher.analysis_modules import (
    ActionabilityAnalysis,
    AudienceAppropriatenessAnalysis,
    CognitiveAnalysis,
    ComplexityAnalysis,
    ControversialityAnalysis,
    CulturalContextAnalysis,
    EmotionalPolarityAnalysis,
    EthicalConsiderationsAnalysis,
    FormalismAnalysis,
    GenreAnalysis,
    HumorAnalysis,
    IntentionalityAnalysis,
    InteractivityAnalysis,
    LexicalDiversityAnalysis,
    ModalityAnalysis,
    MultimodalityAnalysis,
    NarrativeStyleAnalysis,
    NoveltyAnalysis,
    ObjectivityAnalysis,
    PersuasivenessAnalysis,
    QuantitativeAnalysis,
    QualitativeAnalysis,
    ReadabilityAnalysis,
    ReliabilityAnalysis,
    SentimentAnalysis,
    SocialOrientationAnalysis,
    SpecificityAnalysis,
    SpatialAnalysis,
    SyntacticComplexityAnalysis,
    TemporalAnalysis,
)

from publisher.aspect_based_metadata_generator import generate_aspect_based_metadata

# Get system resources
TOTAL_RAM_GB = psutil.virtual_memory().total / (1024**3)
AVAILABLE_RAM_GB = psutil.virtual_memory().available / (1024**3)
CPU_COUNT = psutil.cpu_count()

print(f"🚀 AWS Resources:")
print(f"   Total RAM: {TOTAL_RAM_GB:.1f} GB")
print(f"   Available RAM: {AVAILABLE_RAM_GB:.1f} GB") 
print(f"   CPU Cores: {CPU_COUNT}")

# AWS-optimized chunk sizing (much larger than laptop's 1000 chars)
if AVAILABLE_RAM_GB > 100:
    DEFAULT_CHUNK_SIZE = 0  # No chunking - process entire documents
elif AVAILABLE_RAM_GB > 50:
    DEFAULT_CHUNK_SIZE = 100000  # 100k chars (100x laptop size)
elif AVAILABLE_RAM_GB > 20:
    DEFAULT_CHUNK_SIZE = 50000   # 50k chars (50x laptop size)
else:
    DEFAULT_CHUNK_SIZE = 10000   # 10k chars (10x laptop size)

print(f"   Recommended chunk size: {'No chunking' if DEFAULT_CHUNK_SIZE == 0 else f'{DEFAULT_CHUNK_SIZE:,} chars'}")


def get_analysis_modules():
    """Get all 30 analysis modules (same as publisher_app.py)."""
    return [
        ActionabilityAnalysis,
        AudienceAppropriatenessAnalysis,
        CognitiveAnalysis,
        ComplexityAnalysis,
        ControversialityAnalysis,
        CulturalContextAnalysis,
        EmotionalPolarityAnalysis,
        EthicalConsiderationsAnalysis,
        FormalismAnalysis,
        GenreAnalysis,
        HumorAnalysis,
        IntentionalityAnalysis,
        InteractivityAnalysis,
        LexicalDiversityAnalysis,
        ModalityAnalysis,
        MultimodalityAnalysis,
        NarrativeStyleAnalysis,
        NoveltyAnalysis,
        ObjectivityAnalysis,
        PersuasivenessAnalysis,
        QuantitativeAnalysis,
        QualitativeAnalysis,
        ReadabilityAnalysis,
        ReliabilityAnalysis,
        SentimentAnalysis,
        SocialOrientationAnalysis,
        SpecificityAnalysis,
        SpatialAnalysis,
        SyntacticComplexityAnalysis,
        TemporalAnalysis,
    ]


def aggregate_results(existing_results, new_results, categorical_counts):
    """Aggregate results across chunks (same logic as publisher_app.py)."""
    for key, value in new_results.items():
        if key in existing_results:
            if isinstance(value, float):
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


def analyze_text_aws_optimized(text, chunk_size=0):
    """
    Analyze text using AWS-optimized chunking.
    
    chunk_size=0 means no chunking (analyze entire text at once)
    """
    analysis_modules = get_analysis_modules()
    
    if chunk_size == 0:
        # No chunking - analyze entire text at once (AWS power!)
        print(f"🔥 No chunking - analyzing {len(text):,} characters at once")
        chunks = [text]
    else:
        # Use larger chunks than laptop version
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        print(f"📦 Using {len(chunks)} chunks of ~{chunk_size:,} characters each")
    
    analysis_results = {}
    categorical_counts = {}
    
    # Process each chunk
    for chunk_idx, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
        if not chunk.strip():
            continue
            
        # Run all 30 analysis modules on this chunk
        for module in tqdm(analysis_modules, desc=f"Chunk {chunk_idx+1}/{len(chunks)}", leave=False):
            try:
                analysis_instance = module(chunk)
                result = analysis_instance.analyze()
                analysis_results = aggregate_results(analysis_results, result, categorical_counts)
            except Exception as e:
                print(f"Warning: {module.__name__} failed on chunk {chunk_idx}: {e}")
                # Continue with other modules
                continue
    
    # Add data hash (same as publisher_app.py)
    data_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    analysis_results["data_hash"] = data_hash
    
    # Generate final metadata with encryption (same as publisher_app.py)
    encryption_key = get_random_bytes(16)
    aspect_based_metadata = generate_aspect_based_metadata(analysis_results, encryption_key)
    
    return {
        'analysis_results': analysis_results,
        'aspect_based_metadata': aspect_based_metadata,
        'encryption_key': encryption_key.hex()  # Convert to hex for JSON serialization
    }


def process_batch_aws_style(input_lines, chunk_size, progress_interval=1000):
    """Process all lines with AWS-optimized batching."""
    results = []
    
    for i, line in enumerate(tqdm(input_lines, desc="Processing documents")):
        try:
            obj = json.loads(line.strip())
            
            if 'text' not in obj or not obj['text'].strip():
                obj['aspects'] = {}
                obj['metadata'] = None
            else:
                # Run the full ABMS analysis
                analysis_result = analyze_text_aws_optimized(obj['text'], chunk_size)
                
                # Add results to object
                obj['aspects'] = analysis_result['analysis_results']
                obj['aspect_based_metadata'] = analysis_result['aspect_based_metadata']
                obj['encryption_key'] = analysis_result['encryption_key']
            
            results.append(obj)
            
            # Memory management for very large datasets
            if i % progress_interval == 0 and i > 0:
                memory_usage = psutil.virtual_memory().percent
                if memory_usage > 80:
                    print(f"⚠️  Memory usage: {memory_usage:.1f}% - consider smaller batches")
                    gc.collect()
            
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON at line {i+1}: {e}")
            continue
        except Exception as e:
            print(f"Warning: Error processing line {i+1}: {e}")
            traceback.print_exc()
            continue
    
    return results


def main():
    parser = argparse.ArgumentParser(description="AWS-optimized ABMS batch encoder")
    parser.add_argument("input", help="Input JSONL file")
    parser.add_argument("output", help="Output JSONL file")
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE,
                       help=f"Character chunk size (0=no chunking, default={DEFAULT_CHUNK_SIZE})")
    parser.add_argument("--progress-interval", type=int, default=1000,
                       help="Show progress every N documents")
    
    args = parser.parse_args()
    
    print(f"🎯 Configuration:")
    print(f"   Input: {args.input}")
    print(f"   Output: {args.output}")
    print(f"   Chunk size: {'No chunking' if args.chunk_size == 0 else f'{args.chunk_size:,} chars'}")
    
    # Create output directory
    pathlib.Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    # Read all input data (AWS has plenty of RAM!)
    print(f"📖 Loading {args.input}...")
    with open(args.input, 'r') as f:
        input_lines = f.readlines()
    
    print(f"📊 Loaded {len(input_lines):,} documents into memory")
    
    # Process all documents
    print("⚡ Starting analysis...")
    results = process_batch_aws_style(input_lines, args.chunk_size, args.progress_interval)
    
    # Write results
    print(f"💾 Writing {len(results):,} results...")
    with open(args.output, 'w') as f:
        for obj in tqdm(results, desc="Writing output"):
            f.write(json.dumps(obj) + '\n')
    
    print(f"✅ Completed! {len(results):,} documents processed")
    
    # Show sample output
    if results:
        sample = results[0]
        aspects = sample.get('aspects', {})
        print(f"\n📈 Sample output:")
        print(f"   Text preview: {sample.get('text', '')[:100]}...")
        print(f"   Aspects found: {len(aspects)}")
        print(f"   Sample aspects: {list(aspects.keys())[:5]}")
        print(f"   Has metadata: {'aspect_based_metadata' in sample}")
        
        # Performance stats
        final_memory = psutil.virtual_memory().percent
        print(f"   Final memory usage: {final_memory:.1f}%")


if __name__ == "__main__":
    main()
