#!/usr/bin/env python3
"""
Comprehensive test suite for ABMS (Aspect-Based Metadata System)
Tests each analysis module with diverse text samples
"""

import json
import sys
import pathlib

# Test samples designed to trigger specific aspect behaviors
TEST_SAMPLES = [
    # Actionability tests
    {
        "id": "action_high",
        "text": "You must immediately implement these five steps: First, analyze the data. Second, create a report. Third, present findings. Fourth, get approval. Fifth, execute the plan.",
        "expected": {"actionability": "high", "quantitative": "high"}
    },
    {
        "id": "action_low", 
        "text": "The sunset painted the sky in shades of orange and pink. Clouds drifted lazily across the horizon as birds returned to their nests.",
        "expected": {"actionability": "low", "quantitative": "low"}
    },
    
    # Social orientation tests
    {
        "id": "social_collective",
        "text": "We must work together as a team. Our collective efforts will ensure everyone benefits. Let's collaborate and support each other to achieve our shared goals.",
        "expected": {"social_orientation": "collective"}
    },
    {
        "id": "social_individual",
        "text": "I achieved my personal best today. My individual performance exceeded expectations. I focused on my own goals and accomplished what I set out to do.",
        "expected": {"social_orientation": "individual"}
    },
    
    # Specificity tests
    {
        "id": "specific_high",
        "text": "The meeting is scheduled for March 15, 2024 at 2:30 PM EST in Conference Room B on the 3rd floor. Please bring the Q1 financial report showing the 23.7% revenue increase.",
        "expected": {"specificity": "high", "temporal": "high", "quantitative": "high"}
    },
    {
        "id": "specific_low",
        "text": "Things have been going well lately. The situation seems to be improving somewhat. There might be some changes coming soon that could affect various aspects.",
        "expected": {"specificity": "low", "temporal": "low"}
    },
    
    # Controversiality tests
    {
        "id": "controversial_high",
        "text": "This divisive policy has sparked fierce debate. Supporters claim it will save the economy while critics argue it will destroy fundamental rights. The heated arguments have split communities.",
        "expected": {"controversiality": "high", "sentiment": "mixed"}
    },
    {
        "id": "controversial_low",
        "text": "Water is essential for life. Most people agree that staying hydrated is important for health. Drinking adequate water helps maintain bodily functions.",
        "expected": {"controversiality": "low"}
    },
    
    # Sentiment tests
    {
        "id": "sentiment_positive",
        "text": "What an absolutely fantastic achievement! I'm thrilled and delighted by this wonderful success. Everything worked out perfectly and exceeded our wildest dreams!",
        "expected": {"sentiment": "positive", "emotional_polarity": "high"}
    },
    {
        "id": "sentiment_negative", 
        "text": "This is a terrible disaster. Everything failed miserably. I'm extremely disappointed and frustrated by this awful outcome. Nothing went according to plan.",
        "expected": {"sentiment": "negative", "emotional_polarity": "high"}
    },
    
    # Readability tests
    {
        "id": "readability_simple",
        "text": "The cat sat on the mat. It was a nice day. The sun was bright. Birds sang in the trees. Children played in the park.",
        "expected": {"readability": "high", "audience": "children"}
    },
    {
        "id": "readability_complex",
        "text": "The epistemological ramifications of quantum entanglement necessitate a paradigmatic reconsideration of spatiotemporal locality, fundamentally challenging our ontological presuppositions regarding the nature of reality.",
        "expected": {"readability": "low", "audience": "graduate"}
    },
    
    # Genre tests
    {
        "id": "genre_news",
        "text": "WASHINGTON - The Federal Reserve announced today that interest rates will remain unchanged. Fed Chair Jerome Powell cited economic indicators suggesting stable growth. Markets responded positively to the news.",
        "expected": {"genre": "news", "formalism": "high"}
    },
    {
        "id": "genre_story",
        "text": "Once upon a time in a distant kingdom, there lived a brave knight named Sir Edmund. He embarked on a perilous quest to save the princess from the dragon's lair.",
        "expected": {"genre": "narrative", "narrative_style": "third_person"}
    },
    
    # Humor tests
    {
        "id": "humor_high",
        "text": "Why don't scientists trust atoms? Because they make up everything! I told my wife she was drawing her eyebrows too high. She looked surprised!",
        "expected": {"humor": "high"}
    },
    
    # Multimodality tests
    {
        "id": "multimodal_references",
        "text": "As shown in Figure 3 above, the graph clearly illustrates the trend. See Table 2.1 for detailed statistics. The accompanying video demonstrates the process step by step.",
        "expected": {"multimodality": "high", "modality": "multimedia"}
    }
]

def create_test_jsonl(output_file="test_comprehensive.jsonl"):
    """Create a JSONL file with all test samples"""
    with open(output_file, 'w') as f:
        for sample in TEST_SAMPLES:
            # Only write id, text, and expected to the JSONL
            data = {
                "id": sample["id"],
                "text": sample["text"],
                "expected": sample["expected"]
            }
            f.write(json.dumps(data) + '\n')
    print(f"Created {output_file} with {len(TEST_SAMPLES)} test samples")

def analyze_results(results_file, verbose=False):
    """Analyze the results and check if they match expectations"""
    print("\n" + "="*80)
    print("ABMS TEST RESULTS ANALYSIS")
    print("="*80)
    
    with open(results_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            sample_id = data.get('id', 'unknown')
            aspects = data.get('aspects', {})
            expected = data.get('expected', {})
            
            print(f"\n[{sample_id}]")
            print(f"Text: {data.get('text', '')[:60]}...")
            
            if verbose:
                print("\nAll aspects:")
                for key, value in sorted(aspects.items()):
                    if key != 'data_hash':
                        if isinstance(value, float):
                            print(f"  {key:35} {value:8.4f}")
                        else:
                            print(f"  {key:35} {value}")
            
            # Check expectations
            if expected:
                print("\nExpectation checks:")
                for exp_key, exp_value in expected.items():
                    actual_key = exp_key + "_analysis" if not exp_key.endswith("_analysis") else exp_key
                    if actual_key in aspects:
                        actual = aspects[actual_key]
                        
                        # Interpret the expectation
                        if exp_value in ["high", "positive", "collective"]:
                            threshold = 0.7
                            passed = actual > threshold if isinstance(actual, (int, float)) else str(actual).lower() == exp_value.lower()
                        elif exp_value in ["low", "negative", "individual"]:
                            threshold = 0.3
                            passed = actual < threshold if isinstance(actual, (int, float)) else str(actual).lower() == exp_value.lower()
                        else:
                            passed = str(actual).lower() == exp_value.lower()
                        
                        status = "✓" if passed else "✗"
                        if isinstance(actual, float):
                            print(f"  {status} {exp_key}: expected {exp_value}, got {actual:.4f}")
                        else:
                            print(f"  {status} {exp_key}: expected {exp_value}, got {actual}")

def generate_benchmark_report(results_file, output_file="benchmark_report.md"):
    """Generate a markdown report of the benchmark results"""
    report = []
    report.append("# ABMS Benchmark Report\n")
    report.append("## Summary\n")
    
    # Calculate success rates for each aspect
    aspect_results = {}
    total_tests = 0
    total_passed = 0
    
    with open(results_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            expected = data.get('expected', {})
            aspects = data.get('aspects', {})
            
            for exp_key, exp_value in expected.items():
                actual_key = exp_key + "_analysis" if not exp_key.endswith("_analysis") else exp_key
                if actual_key in aspects:
                    if exp_key not in aspect_results:
                        aspect_results[exp_key] = {"total": 0, "passed": 0}
                    
                    aspect_results[exp_key]["total"] += 1
                    total_tests += 1
                    
                    # Check if passed (simplified logic)  
                    actual = aspects[actual_key]
                    if isinstance(actual, float):
                        if exp_value in ["high", "positive"] and actual > 0.7:
                            aspect_results[exp_key]["passed"] += 1
                            total_passed += 1
                        elif exp_value in ["low", "negative"] and actual < 0.3:
                            aspect_results[exp_key]["passed"] += 1
                            total_passed += 1
    
    report.append(f"- Total tests: {total_tests}\n")
    report.append(f"- Tests passed: {total_passed}\n")
    report.append(f"- Success rate: {(total_passed/total_tests*100):.1f}%\n\n")
    
    report.append("## Results by Aspect\n\n")
    report.append("| Aspect | Tests | Passed | Success Rate |\n")
    report.append("|--------|-------|--------|-------------|\n")
    
    for aspect, results in sorted(aspect_results.items()):
        success_rate = results["passed"] / results["total"] * 100
        report.append(f"| {aspect} | {results['total']} | {results['passed']} | {success_rate:.1f}% |\n")
    
    with open(output_file, 'w') as f:
        f.writelines(report)
    
    print(f"\nBenchmark report saved to {output_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ABMS Test Suite')
    parser.add_argument('--create', action='store_true', help='Create test JSONL file')
    parser.add_argument('--analyze', help='Analyze results file')
    parser.add_argument('--verbose', action='store_true', help='Show all aspect scores')
    parser.add_argument('--benchmark', help='Generate benchmark report from results')
    
    args = parser.parse_args()
    
    if args.create:
        create_test_jsonl()
    elif args.analyze:
        analyze_results(args.analyze, args.verbose)
    elif args.benchmark:
        generate_benchmark_report(args.benchmark)
    else:
        print("Usage:")
        print("  python test_abms.py --create                    # Create test samples")
        print("  python test_abms.py --analyze results.jsonl     # Analyze results")
        print("  python test_abms.py --benchmark results.jsonl   # Generate report")
