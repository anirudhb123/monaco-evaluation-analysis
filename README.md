# Monaco Evaluation Analysis

A comprehensive analysis toolkit for evaluating Large Language Model performance on the Monaco benchmark dataset. This repository provides tools for performance breakdown analysis, failure pattern identification, and detailed comparison across different models.

## 🔍 Overview

This repository contains analysis tools and results for evaluating LLMs on Monaco, a benchmark of complex multi-document reasoning questions. The analysis focuses on understanding model performance patterns, identifying failure modes, and providing detailed breakdowns by operation type and complexity.

## 📊 Key Results

- **GPT-5**: 69.33% F1 (537 valid questions), 77.00% precision, 68.00% recall
- **Gemini 2.5 Pro**: 70.08% F1 (538 valid questions), 74.78% precision, 70.03% recall
- **36 questions** where both models completely failed (F1=0)
- Strong correlation between failure patterns and filter+aggregate operations

## 🛠️ Core Analysis Tools

### Main Analysis Scripts

- **`llm_performance_breakdown.py`** - Comprehensive performance analysis with tokenization
- **`find_common_failures.py`** - Identifies and analyzes questions where multiple models fail
- **`merge_results.py`** - Merges evaluation results from multiple model runs

### Evaluation Scripts

- **`run_gemini_oracle.py`** - Evaluate Gemini models on Monaco with oracle documents
- **`run_oracle_retrieval_scalable.py`** - Scalable evaluation pipeline for any LLM
- **`re_evaluate_with_gpt4_judge.py`** - Re-score results with different judge models

### Utilities

- **`utils.py`** - Core utility functions for data loading and processing
- **`operation_identifier.py`** - Identifies reasoning operation types in questions
- **`decomposition_utils.py`** - Parses question decomposition steps
- **`consts.py`** - Constants and configuration

## 📁 Repository Structure

```
├── analysis_results_gpt5/           # GPT-5 performance analysis results
├── analysis_results_gemini25pro/    # Gemini 2.5 Pro performance analysis results
├── merged_results/                  # Combined evaluation results
├── llm_performance_breakdown.py     # Main analysis script
├── find_common_failures.py          # Failure analysis tool
├── monaco_version_1_release.json    # Monaco dataset
├── question_stats_breakdown.json    # Question metadata and statistics
├── docs_oracle_retrieval_2025.jsonl # Oracle documents for questions
└── requirements_analysis.txt        # Python dependencies
```

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/anirudhb123/monaco-evaluation-analysis.git
cd monaco-evaluation-analysis
pip install -r requirements_analysis.txt
```

### Run Performance Analysis

```bash
# Analyze existing results
python llm_performance_breakdown.py merged_results/monaco_gpt5_gpt41judge.json
python llm_performance_breakdown.py merged_results/monaco_gemini25pro_gpt41judge.json

# Find common failure patterns
python find_common_failures.py
```

### Evaluate New Models

```bash
# Evaluate Gemini models
python run_gemini_oracle.py --model gemini-2.5-pro --questions 100

# Evaluate other models (requires API setup)
python run_oracle_retrieval_scalable.py --model your-model-name
```

## 📈 Analysis Features

### Performance Breakdown
- **Tokenization analysis** using tiktoken for accurate context length measurement
- **Operation type classification** (filter, aggregate, arithmetic, comparison, boolean)
- **Complexity metrics** (number of documents, decomposition steps, subquestions)
- **Cross-model comparison** with statistical significance testing

### Failure Analysis
- **Common failure identification** across multiple models
- **F1=0 analysis** for questions no model can solve
- **Pattern recognition** in failure modes by operation type
- **Detailed failure case studies** with supporting documents

### Data Quality
- **Proper NaN handling** for missing recall/F1 data
- **Validation of evaluation metrics** 
- **Context length verification** with token-level precision

## 🔬 Key Insights

### Model Comparison
- Gemini 2.5 Pro shows slight edge in F1 score (70.08% vs 69.33%)
- GPT-5 demonstrates higher precision (77.00% vs 74.78%)
- Similar failure patterns across both models

### Failure Patterns
- **58.3% of common failures** involve filter operations
- **58.3% of common failures** involve aggregate operations
- Questions with >60 documents show higher failure rates
- Zero comparison operations in common failure set

### Complexity Analysis
- Average 72K-73K tokens per question context
- Questions with 7+ operators show decreased performance
- Filter+aggregate combinations particularly challenging

## 📊 Results Files

### Analysis Results
- `analysis_results_*/comprehensive_analysis_data.csv` - Complete performance breakdown
- Results include F1, precision, recall, tokenization data, and operation analysis

### Input Data
- `merged_results/` - Original model evaluation results with GPT-4.1 judge scores
- `monaco_version_1_release.json` - Complete Monaco dataset
- `question_stats_breakdown.json` - Question metadata and complexity metrics

## 🔧 Technical Details

### Requirements
- Python 3.8+
- tiktoken for tokenization
- pandas, numpy for analysis
- matplotlib, seaborn for visualization

### Data Processing
- Handles JSON and JSONL formats
- Robust error handling for malformed evaluation data
- Efficient processing of large document collections
- Memory-optimized for analysis of 1000+ questions

## 📝 Citation

If you use this analysis toolkit in your research, please cite:

```bibtex
@misc{monaco-evaluation-analysis,
  title={Monaco Evaluation Analysis: LLM Performance Breakdown Tools},
  author={Anirudh Bharadwaj},
  year={2025},
  url={https://github.com/anirudhb123/monaco-evaluation-analysis}
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests for:
- Additional analysis tools
- Support for new model APIs
- Visualization improvements
- Bug fixes and optimizations

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
