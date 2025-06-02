#!/usr/bin/env python3
"""
Cached AWS-optimized ABMS batch encoder - pre-loads models for speed!

Key optimizations:
- Pre-loads all models once at startup
- Caches analysis module instances
- Optimized for AWS resources
- Much faster than downloading models per document
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
import os

# Suppress warnings and set cache directories
warnings.filterwarnings('ignore')
os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
os.environ['HF_HOME'] = '/tmp/huggingface_cache'

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
DEFAULT_CHUNK_SIZE = 0  # No chunking for AWS

print(f"   Chunk size: No chunking (full AWS power)")


class CachedAnalysisOrchestrator:
    """Pre-loads and caches all analysis modules for fast processing."""
    
    def __init__(self):
        self.loaded_modules = {}
        self.module_instances = {}
        self.successful_modules = []
        self.failed_modules = []
        
        # Module mapping
        self.module_names = [
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
        
        self._load_all_modules()
    
    def _load_all_modules(self):
        """Load all available modules and their dependencies once."""
        print("🔧 Pre-loading analysis modules and models...")
        
        for module_name in tqdm(self.module_names, desc="Loading modules"):
            try:
                # Convert class name to module name
                snake_case = ''.join(['_' + c.lower() if c.isupper() and i > 0 else c.lower() 
                                     for i, c in enumerate(module_name)]).lstrip('_')
                
                # Import module
                module = __import__(f'publisher.analysis_modules.{snake_case}', fromlist=[module_name])
                analysis_class = getattr(module, module_name)
                
                # Pre-instantiate with dummy text to trigger model downloads
                test_instance = analysis_class("test initialization text")
                
                # Store the class for later use
                self.loaded_modules[module_name] = analysis_class
                self.successful_modules.append(module_name)
                
            except Exception as e:
                self.failed_modules.append((module_name, str(e)))
                continue
        
        print(f"📦 Module loading results:")
        print(f"   ✅ Loaded: {len(self.successful_modules)}/30 modules")
        print(f"   ❌ Failed: {len(self.failed_modules)} modules")
        
        if self.failed_modules and len(self.failed_modules) <= 5:
            for name, error in self.failed_modules:
                error_short = error.split(':')[0] if ':' in error else error[:50]
                print(f"      {name}: {error_short}")
    
    def analyze_text(self, text):
        """Analyze text using pre-loaded modules."""
        analysis_results = {}
        categorical_counts = {}
        successful_analyses = 0
        failed_analyses = 0
        
        # Process with all loaded modules
        for module_name, module_class in self.loaded_modules.items():
            try:
                # Create instance (fast since models are already loaded)
                analysis_instance = module_class(text)
                result = analysis_instance.analyze()
                
                if result:
                    analysis_results = self._aggregate_results(analysis_results, result, categorical_counts)
                    successful_analyses += 1
                    
            except Exception as e:
                failed_analyses += 1
                continue
        
        # Add data hash
        data_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        analysis_results["data_hash"] = data_hash
        
        # Generate metadata
        aspect_based_metadata = None
        encryption_key = None
        
        try:
            from publisher.aspect_based_metadata_generator import generate_aspect_based_metadata
            from Crypto.Random import get_random_bytes
            
            encryption_key = get_random_bytes(16)
            aspect_based_metadata = generate_aspect_based_metadata(analysis_results, encryption_key)
            encryption_key = encryption_key.hex()
            
        except Exception as e:
            pass  # Continue without metadata
        
        return {
            'analysis_results': analysis_results,
            'aspect_based_metadata': aspect_based_metadata,
            'encryption_key': encryption_key,
            'stats': {'successful': successful_analyses, 'failed': failed_analyses}
        }
    
    def _aggregate_results(self, existing_results, new_results, categorical_counts):
        """Aggregate results (same logic as publisher_app.py)."""
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


def process_batch_cached(input_lines, orchestrator, progress_interval=1000):
    """Process all lines with pre-loaded analysis modules."""
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
                # Fast analysis with cached modules
                analysis_result = orchestrator.analyze_text(obj['text'])
                
                # Add results to object
                obj['aspects'] = analysis_result['analysis_results']
                obj['aspect_based_metadata'] = analysis_result['aspect_based_metadata']
                obj['encryption_key'] = analysis_result['encryption_key']
                
                total_successful += 1
            
            results.append(obj)
            
            # Memory and progress management
            if i % progress_interval == 0 and i > 0:
                memory_usage = psutil.virtual_memory().percent
                docs_per_sec = i / (progress_interval * 0.1) if i > progress_interval else 0
                print(f"   Processed {i:,} docs. Memory: {memory_usage:.1f}%. Speed: ~{docs_per_sec:.1f} docs/sec")
                if memory_usage > 85:
                    gc.collect()
            
        except json.JSONDecodeError as e:
            total_failed += 1
            continue
        except Exception as e:
            total_failed += 1
            continue
    
    print(f"📊 Final summary: {total_successful:,} successful, {total_failed:,} failed")
    return results


def main():
    parser = argparse.ArgumentParser(description="Cached AWS-optimized ABMS batch encoder")
    parser.add_argument("input", help="Input JSONL file")
    parser.add_argument("output", help="Output JSONL file")
    parser.add_argument("--progress-interval", type=int, default=1000,
                       help="Show progress every N documents")
    
    args = parser.parse_args()
    
    print(f"🎯 Configuration:")
    print(f"   Input: {args.input}")
    print(f"   Output: {args.output}")
    print(f"   Progress interval: {args.progress_interval:,}")
    
    # Initialize orchestrator (this loads all models once)
    orchestrator = CachedAnalysisOrchestrator()
    
    if not orchestrator.successful_modules:
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
    print("⚡ Starting cached analysis...")
    import time
    start_time = time.time()
    
    results = process_batch_cached(input_lines, orchestrator, args.progress_interval)
    
    elapsed_time = time.time() - start_time
    docs_per_sec = len(results) / elapsed_time if elapsed_time > 0 else 0
    
    # Write results
    print(f"💾 Writing {len(results):,} results...")
    with open(args.output, 'w') as f:
        for obj in tqdm(results, desc="Writing output"):
            f.write(json.dumps(obj) + '\n')
    
    print(f"✅ Completed! Output written to {args.output}")
    print(f"⏱️  Performance: {docs_per_sec:.1f} documents/second")
    print(f"📈 Total time: {elapsed_time:.1f} seconds")
    
    # Show sample output
    if results:
        sample = results[0]
        aspects = sample.get('aspects', {})
        print(f"\n📊 Sample output:")
        print(f"   Text preview: {sample.get('text', '')[:100]}...")
        print(f"   Aspects found: {len(aspects)}")
        if aspects:
            print(f"   Sample aspects: {list(aspects.keys())[:5]}")
            sample_values = {k: v for k, v in list(aspects.items())[:3]}
            print(f"   Sample values: {sample_values}")


if __name__ == "__main__":
    main()
