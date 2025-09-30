#!/usr/bin/env python3
"""
Merge multiple MoNaCo Oracle evaluation result files.
Usage: python merge_results.py file1.json file2.json ... --output merged_results.json
"""

import json
import argparse
import sys
from typing import List, Dict, Any

def merge_oracle_results(input_files: List[str], output_file: str):
    """Merge multiple Oracle evaluation result files."""
    
    merged_results = []
    total_processed = 0
    total_score = 0.0
    models_used = set()
    
    print(f"📂 Merging {len(input_files)} result files...")
    
    for i, file_path in enumerate(input_files):
        print(f"📖 Reading {file_path}...")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Extract results and metadata
            results = data.get("results", [])
            metadata = data.get("metadata", {})
            
            print(f"   Found {len(results)} results")
            
            # Append results
            merged_results.extend(results)
            
            # Accumulate totals
            total_processed += metadata.get("processed_questions", 0)
            total_score += metadata.get("average_judge_score", 0) * metadata.get("processed_questions", 0)
            models_used.add(metadata.get("model", "unknown"))
            
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            continue
    
    # Calculate final average score
    final_avg_score = total_score / total_processed if total_processed > 0 else 0.0
    
    # Create merged output
    merged_data = {
        "metadata": {
            "total_questions": len(merged_results),
            "processed_questions": total_processed,
            "average_judge_score": final_avg_score,
            "models_used": list(models_used),
            "source_files": input_files,
            "merged_from": len(input_files)
        },
        "results": merged_results
    }
    
    # Save merged results
    with open(output_file, 'w') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Merged results saved to: {output_file}")
    print(f"📊 Total questions: {len(merged_results)}")
    print(f"🏆 Average judge score: {final_avg_score:.3f}")
    
    return merged_data

def main():
    parser = argparse.ArgumentParser(description="Merge MoNaCo Oracle evaluation results")
    parser.add_argument("input_files", nargs="+", help="Input result files to merge")
    parser.add_argument("--output", default="merged_oracle_results.json", 
                       help="Output file for merged results")
    
    args = parser.parse_args()
    
    # Validate input files exist
    for file_path in args.input_files:
        try:
            with open(file_path, 'r') as f:
                pass
        except FileNotFoundError:
            print(f"❌ Error: File not found: {file_path}")
            sys.exit(1)
    
    # Merge the results
    merge_oracle_results(args.input_files, args.output)

if __name__ == "__main__":
    main() 