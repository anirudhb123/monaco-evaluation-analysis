#!/usr/bin/env python3
"""
LLM Performance Breakdown Analysis for MoNaCo Benchmark (with Oracle docs)

Adds:
- Oracle docs loading
- Raw doc count
- Cumulative context length (tokens + words)
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter
import os
import sys
import warnings
import tiktoken

warnings.filterwarnings("ignore")

# Import local modules
from decomposition_utils import decomposition_to_steps
from operation_identifier import identify_operation
from utils import load_json


class MoNaCoPerformanceAnalyzer:
    """Comprehensive analyzer for MoNaCo LLM performance breakdown."""

    def __init__(
        self,
        results_file: str,
        dataset_file: str = "/mnt/nlpgridio3/data/anirudh2/monaco/monaco_version_1_release.json",
        question_stats_file: str = "/mnt/nlpgridio3/data/anirudh2/monaco/question_stats_breakdown.json",
        oracle_docs_file: str = "/mnt/nlpgridio3/data/anirudh2/monaco/docs_oracle_retrieval_2025.jsonl",
    ):
        """Initialize the analyzer with data files."""
        self.dataset_file = dataset_file
        self.question_stats_file = question_stats_file
        self.results_file = results_file
        self.oracle_docs_file = oracle_docs_file

        # Validate files
        for f in [self.dataset_file, self.results_file, self.oracle_docs_file]:
            if not os.path.exists(f):
                print(f"❌ File not found: {f}")
                sys.exit(1)

        self.has_question_stats = os.path.exists(self.question_stats_file)
        if not self.has_question_stats:
            print(f"⚠️ Question stats not found: {self.question_stats_file}")

        # Data holders
        self.dataset = None
        self.question_stats = None
        self.results_data = None
        self.oracle_docs = None
        self.analysis_df = None

    def load_data(self):
        """Load dataset, stats, results, and oracle docs."""
        print("🔄 Loading data files...")

        self.dataset = load_json(self.dataset_file)
        self.results_data = load_json(self.results_file)
        if self.has_question_stats:
            self.question_stats = load_json(self.question_stats_file)
        else:
            self.question_stats = {}

        # Load oracle docs JSON → {question: [docs]}
        self.oracle_docs = {}
        with open(self.oracle_docs_file, "r") as f:
            content = f.read()
            oracle_data = json.loads(content)
            # The file is a single JSON object with questions as keys
            for question, docs in oracle_data.items():
                self.oracle_docs[question] = docs

        print(f"✅ Loaded {len(self.dataset)} dataset Qs")
        print(f"✅ Loaded {len(self.results_data.get('results', []))} results")
        print(f"✅ Loaded oracle docs for {len(self.oracle_docs)} questions")

    def extract_operator_types(self, decomposition_steps: List[str]) -> List[str]:
        """Extract operator types from decomposition steps."""
        operators = []
        for step in decomposition_steps:
            op = identify_operation(step)
            operators.append(op if op else "qa_model")
        return operators

    def compute_context_tokens(self, docs: List[Dict]) -> int:
        """Compute cumulative token length for docs using tiktoken."""
        if not docs:
            return 0
        enc = tiktoken.get_encoding("cl100k_base")
        total_tokens = 0
        for doc in docs:
            text = doc.get('text', '') if isinstance(doc, dict) else str(doc)
            total_tokens += len(enc.encode(text))
        return total_tokens

    def compute_context_words(self, docs: List[Dict]) -> int:
        """Compute cumulative word length for docs."""
        if not docs:
            return 0
        total_words = 0
        for doc in docs:
            text = doc.get('text', '') if isinstance(doc, dict) else str(doc)
            total_words += len(text.split())
        return total_words

    def create_comprehensive_analysis_dataframe(self) -> pd.DataFrame:
        """Create comprehensive dataframe combining all analysis dimensions."""
        print("🔄 Creating comprehensive analysis dataframe...")

        rows = []
        results_by_question = {
            r.get("question", "").strip(): r
            for r in self.results_data.get("results", [])
        }

        for question_text, result in results_by_question.items():
            evaluation = result.get("evaluation", {})
            scores = evaluation.get("scores", {})
            if not scores:
                continue

            question_data = self.dataset.get(question_text, {})
            stats = self.question_stats.get(question_text, {})

            # Oracle docs
            docs = self.oracle_docs.get(question_text, [])
            num_docs = len(docs)
            context_tokens = self.compute_context_tokens(docs)
            context_words = self.compute_context_words(docs)

            # Decomposition
            decomposition_list = question_data.get("decomposition", [])
            if isinstance(decomposition_list, str):
                decomposition_steps = decomposition_to_steps(decomposition_list)
            else:
                decomposition_steps = decomposition_list
            operators = self.extract_operator_types(decomposition_steps)
            unique_operators = list(set(operators))
            op_counts = Counter(operators)

            # Performance metrics
            judge_score = scores.get("judge_score", 0.0)
            precision = scores.get("precision", 0.0)
            recall = scores.get("recall", np.nan)
            f1_score = scores.get("f1", np.nan)
            
            # Calculate F1 only if we have valid precision and recall
            if pd.isna(f1_score) and not pd.isna(recall) and precision >= 0 and recall >= 0:
                if precision + recall > 0:
                    f1_score = 2 * (precision * recall) / (precision + recall)
                else:
                    f1_score = 0.0
            elif pd.isna(recall):
                # If recall is NaN, F1 should also be NaN
                f1_score = np.nan

            # Calculate question tokens
            enc = tiktoken.get_encoding("cl100k_base")
            question_tokens = len(enc.encode(question_text))

            # Row - focused on operation counts and core metrics
            row = {
                "question": question_text,
                "ex_num": question_data.get("ex_num", ""),
                "judge_score": judge_score,
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "num_docs": num_docs,
                "cumulative_context_tokens": context_tokens,
                "cumulative_context_words": context_words,
                "question_tokens": question_tokens,
                "num_intermediate_answers": stats.get("num_intermediate_answers", 0),
                "operators": operators,
                "unique_operators": unique_operators,
                "num_operators": len(operators),
                "num_unique_operators": len(unique_operators),
                "count_aggregate": op_counts.get("aggregate", 0),
                "count_group": op_counts.get("group", 0),
                "count_filter": sum(op_counts[o] for o in op_counts if "filter" in o),
                "count_arithmetic": op_counts.get("arithmetic", 0),
                "count_comparison": op_counts.get("comparison", 0),
                "count_boolean": op_counts.get("boolean", 0),
                "count_qa_model": op_counts.get("qa_model", 0),
                "count_total_ops": sum(op_counts.values()),
                "num_decomp_steps": len(decomposition_steps),
                "num_subquestions": stats.get("num_subquestions", 0),
                "gpt5_score": stats.get("llm_scores", {}).get("gpt5_zs_no_cot", 0.0),
                "gemini25_pro_score": stats.get("llm_scores", {}).get(
                    "gemini25-pro_zs_no_cot", 0.0
                ),
                "gemini25_flash_score": stats.get("llm_scores", {}).get(
                    "gemini25-flash_zs_no_cot", 0.0
                ),
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        print(f"✅ Created analysis dataframe with {len(df)} rows, {len(df.columns)} cols")
        return df


def main():
    if len(sys.argv) < 2:
        print("Usage: python monaco_analysis.py <results_file>")
        sys.exit(1)

    results_file = sys.argv[1]
    analyzer = MoNaCoPerformanceAnalyzer(results_file)
    analyzer.load_data()
    df = analyzer.create_comprehensive_analysis_dataframe()

    out_csv = "comprehensive_analysis_data.csv"
    df.to_csv(out_csv, index=False)
    print(f"💾 Saved analysis dataframe → {out_csv}")


if __name__ == "__main__":
    main()
