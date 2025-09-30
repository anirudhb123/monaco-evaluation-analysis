#!/usr/bin/env python3
"""
Find questions where both GPT-5 and Gemini 2.5 Pro had F1 scores of 0.
Analyze the common failure patterns between models.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import Counter

def load_both_analyses():
    """Load analysis data for both models and original results."""
    import json
    
    # Load comprehensive analysis
    gpt5_df = pd.read_csv('performance_analysis_results_gpt5_gpt41judge/comprehensive_analysis_data.csv')
    gemini_df = pd.read_csv('performance_analysis_results_gemini25pro_gpt41judge/comprehensive_analysis_data.csv')
    
    # Load original results to get generated answers
    with open('merged_results/monaco_gpt5_gpt41judge.json', 'r') as f:
        gpt5_results = json.load(f)
    
    with open('merged_results/monaco_gemini25pro_gpt41judge.json', 'r') as f:
        gemini_results = json.load(f)
    
    # Create lookup dictionaries for answers and docs
    gpt5_answers = {result['question']: result.get('llm_response', '') for result in gpt5_results['results']}
    gemini_answers = {result['question']: result.get('llm_response', '') for result in gemini_results['results']}
    
    # Get intermediate docs from oracle docs file
    oracle_docs = {}
    try:
        with open('docs_oracle_retrieval_2025.jsonl', 'r') as f:
            content = f.read()
            oracle_data = json.loads(content)
            # The file seems to be a single JSON object with questions as keys
            for question, docs in oracle_data.items():
                oracle_docs[question] = docs
    except Exception as e:
        print(f"Warning: Could not load oracle docs: {e}")
        oracle_docs = {}
    
    # Add answers and docs to dataframes
    gpt5_df['gpt5_answer'] = gpt5_df['question'].map(gpt5_answers)
    gpt5_df['intermediate_docs'] = gpt5_df['question'].map(oracle_docs).apply(lambda x: json.dumps(x) if x else "[]")
    
    gemini_df['gemini_answer'] = gemini_df['question'].map(gemini_answers)
    gemini_df['intermediate_docs'] = gemini_df['question'].map(oracle_docs).apply(lambda x: json.dumps(x) if x else "[]")
    
    return gpt5_df, gemini_df

def find_common_zero_f1(gpt5_df, gemini_df):
    """Find questions where both models had F1 score of 0."""
    # Filter for F1 = 0 in both models, but exclude cases with null/blank recall
    # Also exclude cases where precision is null or both precision and recall are 0 due to missing data
    gpt5_zero = gpt5_df[
        (gpt5_df['f1_score'] == 0.0) & 
        (gpt5_df['recall'].notna()) & 
        (gpt5_df['precision'].notna()) &
        (gpt5_df['recall'] >= 0) &  # Ensure recall is a valid number
        (gpt5_df['precision'] >= 0)  # Ensure precision is a valid number
    ].copy()
    
    gemini_zero = gemini_df[
        (gemini_df['f1_score'] == 0.0) & 
        (gemini_df['recall'].notna()) & 
        (gemini_df['precision'].notna()) &
        (gemini_df['recall'] >= 0) &  # Ensure recall is a valid number
        (gemini_df['precision'] >= 0)  # Ensure precision is a valid number
    ].copy()
    
    print(f"GPT-5 has {len(gpt5_zero)} questions with true F1=0 (excluding null recall/precision)")
    print(f"Gemini 2.5 Pro has {len(gemini_zero)} questions with true F1=0 (excluding null recall/precision)")
    
    # Find intersection based on question text
    common_questions = set(gpt5_zero['question']) & set(gemini_zero['question'])
    print(f"Common F1=0 questions: {len(common_questions)}")
    
    # Get the data for common questions from GPT-5 dataframe
    common_df = gpt5_zero[gpt5_zero['question'].isin(common_questions)].copy()
    
    # Add Gemini scores and generated answer for comparison
    gemini_lookup = gemini_zero.set_index('question')[['precision', 'recall', 'judge_score', 'gemini_answer']].add_suffix('_gemini')
    common_df = common_df.merge(gemini_lookup, left_on='question', right_index=True, how='left')
    
    return common_df, gpt5_zero, gemini_zero

def analyze_common_failure_patterns(common_df):
    """Analyze patterns in questions that both models failed completely."""
    patterns = {
        'score_stats': {
            'gpt5_precision_mean': common_df['precision'].mean(),
            'gpt5_recall_mean': common_df['recall'].mean(),
            'gemini_precision_mean': common_df['precision_gemini'].mean(),
            'gemini_recall_mean': common_df['recall_gemini'].mean(),
            'gpt5_judge_mean': common_df['judge_score'].mean(),
            'gemini_judge_mean': common_df['judge_score_gemini'].mean(),
        },
        'operator_patterns': {
            'has_filter_ops': common_df['has_filter_ops'].sum(),
            'has_aggregate_ops': common_df['has_aggregate_ops'].sum(),
            'has_arithmetic_ops': common_df['has_arithmetic_ops'].sum(),
            'has_comparison_ops': common_df['has_comparison_ops'].sum(),
            'has_boolean_ops': common_df['has_boolean_ops'].sum(),
        },
        'complexity_patterns': {
            'avg_num_docs': common_df['num_docs'].mean(),
            'avg_num_operators': common_df['num_operators'].mean(),
            'avg_num_unique_operators': common_df['num_unique_operators'].mean(),
            'avg_num_decomp_steps': common_df['num_decomp_steps'].mean(),
            'avg_num_subquestions': common_df['num_subquestions'].mean(),
            'avg_question_length': common_df['question_word_count'].mean(),
        },
        'context_bins': Counter(common_df['context_length_bin']),
        'intermediate_answer_bins': Counter(common_df['intermediate_answers_bin']),
        'performance_flags': {
            'is_zero': common_df['is_zero'].sum(),
            'is_low_performance': common_df['is_low_performance'].sum(),
        }
    }
    
    return patterns

def create_comparison_plots(common_df, gpt5_zero, gemini_zero, output_dir):
    """Create comparison plots between models and common failures."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    plt.style.use('seaborn-v0_8')
    fig = plt.figure(figsize=(20, 16))
    
    # Create a 4x3 grid of subplots
    gs = fig.add_gridspec(4, 3, hspace=0.3, wspace=0.3)
    
    # 1. Precision comparison
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.hist(common_df['precision'], bins=20, alpha=0.7, label='GPT-5', color='blue')
    ax1.hist(common_df['precision_gemini'], bins=20, alpha=0.7, label='Gemini 2.5', color='red')
    ax1.set_title('Precision Distribution (Common F1=0)')
    ax1.set_xlabel('Precision')
    ax1.set_ylabel('Count')
    ax1.legend()
    
    # 2. Judge score comparison
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.hist(common_df['judge_score'], bins=20, alpha=0.7, label='GPT-5', color='blue')
    ax2.hist(common_df['judge_score_gemini'], bins=20, alpha=0.7, label='Gemini 2.5', color='red')
    ax2.set_title('Judge Score Distribution (Common F1=0)')
    ax2.set_xlabel('Judge Score')
    ax2.set_ylabel('Count')
    ax2.legend()
    
    # 3. Model-specific F1=0 counts by operators
    ax3 = fig.add_subplot(gs[0, 2])
    op_types = ['has_filter_ops', 'has_aggregate_ops', 'has_arithmetic_ops', 
                'has_comparison_ops', 'has_boolean_ops']
    gpt5_counts = [gpt5_zero[op].sum() for op in op_types]
    gemini_counts = [gemini_zero[op].sum() for op in op_types]
    common_counts = [common_df[op].sum() for op in op_types]
    
    x = range(len(op_types))
    width = 0.25
    ax3.bar([i - width for i in x], gpt5_counts, width, label='GPT-5 Only', alpha=0.8)
    ax3.bar(x, gemini_counts, width, label='Gemini Only', alpha=0.8)
    ax3.bar([i + width for i in x], common_counts, width, label='Both Models', alpha=0.8)
    
    ax3.set_title('F1=0 Examples by Operator Type')
    ax3.set_ylabel('Count')
    ax3.set_xticks(x)
    ax3.set_xticklabels([op.replace('has_', '').replace('_ops', '') for op in op_types], rotation=45)
    ax3.legend()
    
    # 4. Context length distribution comparison
    ax4 = fig.add_subplot(gs[1, 0])
    context_counts_common = common_df['context_length_bin'].value_counts()
    context_counts_gpt5 = gpt5_zero['context_length_bin'].value_counts()
    context_counts_gemini = gemini_zero['context_length_bin'].value_counts()
    
    # Get all unique bins
    all_bins = sorted(set(context_counts_common.index) | set(context_counts_gpt5.index) | set(context_counts_gemini.index))
    
    gpt5_vals = [context_counts_gpt5.get(bin_name, 0) for bin_name in all_bins]
    gemini_vals = [context_counts_gemini.get(bin_name, 0) for bin_name in all_bins]
    common_vals = [context_counts_common.get(bin_name, 0) for bin_name in all_bins]
    
    x = range(len(all_bins))
    width = 0.25
    ax4.bar([i - width for i in x], gpt5_vals, width, label='GPT-5 F1=0', alpha=0.8)
    ax4.bar(x, gemini_vals, width, label='Gemini F1=0', alpha=0.8)
    ax4.bar([i + width for i in x], common_vals, width, label='Both F1=0', alpha=0.8)
    
    ax4.set_title('Context Length Distribution')
    ax4.set_ylabel('Count')
    ax4.set_xticks(x)
    ax4.set_xticklabels(all_bins, rotation=45)
    ax4.legend()
    
    # 5. Number of documents vs complexity
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.scatter(common_df['num_docs'], common_df['num_operators'], alpha=0.6, c='purple')
    ax5.set_xlabel('Number of Documents')
    ax5.set_ylabel('Number of Operators')
    ax5.set_title('Document Count vs Operators (Common Failures)')
    
    # 6. Question length vs decomposition steps
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.scatter(common_df['question_word_count'], common_df['num_decomp_steps'], alpha=0.6, c='orange')
    ax6.set_xlabel('Question Word Count')
    ax6.set_ylabel('Decomposition Steps')
    ax6.set_title('Question Length vs Complexity')
    
    # 7. Operator count breakdown for common failures
    ax7 = fig.add_subplot(gs[2, 0])
    operator_counts = ['count_filter', 'count_aggregate', 'count_arithmetic', 'count_comparison', 'count_boolean', 'count_qa_model']
    avg_counts = [common_df[op].mean() for op in operator_counts]
    ax7.bar(range(len(operator_counts)), avg_counts)
    ax7.set_title('Average Operator Counts (Common Failures)')
    ax7.set_ylabel('Average Count')
    ax7.set_xticks(range(len(operator_counts)))
    ax7.set_xticklabels([op.replace('count_', '') for op in operator_counts], rotation=45)
    
    # 8. Intermediate answers distribution
    ax8 = fig.add_subplot(gs[2, 1])
    int_ans_counts = common_df['intermediate_answers_bin'].value_counts()
    ax8.bar(range(len(int_ans_counts)), int_ans_counts.values)
    ax8.set_title('Intermediate Answers Distribution')
    ax8.set_xlabel('Intermediate Answers Bin')
    ax8.set_ylabel('Count')
    ax8.set_xticks(range(len(int_ans_counts)))
    ax8.set_xticklabels(int_ans_counts.index, rotation=45)
    
    # 9. Number of subquestions distribution
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.hist(common_df['num_subquestions'], bins=20, alpha=0.7, color='green')
    ax9.set_title('Subquestions Distribution (Common Failures)')
    ax9.set_xlabel('Number of Subquestions')
    ax9.set_ylabel('Count')
    
    # 10-12. Additional complexity metrics
    ax10 = fig.add_subplot(gs[3, 0])
    ax10.scatter(common_df['num_unique_operators'], common_df['num_operators'], alpha=0.6)
    ax10.set_xlabel('Unique Operators')
    ax10.set_ylabel('Total Operators')
    ax10.set_title('Operator Diversity vs Count')
    
    ax11 = fig.add_subplot(gs[3, 1])
    complexity_score = common_df['num_docs'] + common_df['num_operators'] + common_df['num_decomp_steps']
    ax11.hist(complexity_score, bins=20, alpha=0.7, color='brown')
    ax11.set_title('Combined Complexity Score')
    ax11.set_xlabel('Complexity Score')
    ax11.set_ylabel('Count')
    
    ax12 = fig.add_subplot(gs[3, 2])
    perf_flags = ['is_zero', 'is_low_performance']
    flag_counts = [common_df[flag].sum() for flag in perf_flags]
    ax12.bar(perf_flags, flag_counts)
    ax12.set_title('Performance Flags (Common Failures)')
    ax12.set_ylabel('Count')
    
    plt.suptitle(f'Common F1=0 Failures Analysis: {len(common_df)} Questions', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    # Save plot
    plt.savefig(output_dir / 'common_f1_zero_failures_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.show()

def print_detailed_comparison(common_df, patterns, gpt5_zero, gemini_zero):
    """Print detailed comparison statistics."""
    print(f"\n🔍 Common F1=0 Failures Analysis")
    print("=" * 60)
    print(f"Total questions with F1=0 in both models: {len(common_df)}")
    print(f"GPT-5 only F1=0: {len(gpt5_zero)}")
    print(f"Gemini 2.5 Pro only F1=0: {len(gemini_zero)}")
    
    print(f"\n📊 Score Comparison (Common Failures):")
    print(f"  GPT-5 Precision Mean: {patterns['score_stats']['gpt5_precision_mean']:.3f}")
    print(f"  Gemini Precision Mean: {patterns['score_stats']['gemini_precision_mean']:.3f}")
    print(f"  GPT-5 Judge Score Mean: {patterns['score_stats']['gpt5_judge_mean']:.3f}")
    print(f"  Gemini Judge Score Mean: {patterns['score_stats']['gemini_judge_mean']:.3f}")
    
    print(f"\n🔧 Operator Patterns (Common Failures):")
    for op, count in patterns['operator_patterns'].items():
        print(f"  {op}: {count}/{len(common_df)} ({count/len(common_df)*100:.1f}%)")
    
    print(f"\n📈 Complexity Patterns (Common Failures):")
    for metric, value in patterns['complexity_patterns'].items():
        print(f"  Avg {metric}: {value:.2f}")
    
    print(f"\n📋 Context Length Distribution:")
    for bin_name, count in patterns['context_bins'].most_common():
        print(f"  {bin_name}: {count} ({count/len(common_df)*100:.1f}%)")

def save_common_failures_csv(common_df, output_dir):
    """Save the common failure examples to CSV."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Add rank column
    common_df_copy = common_df.copy()
    common_df_copy['rank'] = range(1, len(common_df_copy) + 1)
    
    # Select only the specified columns
    desired_cols = [
        'rank', 'question', 'gpt5_answer', 'gemini_answer_gemini', 'intermediate_docs',
        'num_docs', 'num_operators', 'num_decomp_steps', 'ex_num', 'is_perfect', 'is_zero', 
        'is_high_performance', 'is_low_performance', 'num_intermediate_answers', 'operators', 
        'unique_operators', 'num_unique_operators', 'has_filter_ops', 'has_aggregate_ops', 
        'has_arithmetic_ops', 'has_comparison_ops', 'has_boolean_ops', 'count_aggregate', 
        'count_filter', 'count_arithmetic', 'count_comparison', 'count_boolean', 'count_qa_model', 
        'count_total_ops', 'num_subquestions', 'has_aggregate_op_flag', 'gpt5_score', 
        'gemini25_pro_score', 'gemini25_flash_score'
    ]
    
    # Filter to only include columns that exist in the dataframe
    available_cols = [col for col in desired_cols if col in common_df_copy.columns]
    missing_cols = [col for col in desired_cols if col not in common_df_copy.columns]
    
    if missing_cols:
        print(f"Note: Missing columns: {missing_cols}")
    
    final_cols = available_cols
    
    common_df_ordered = common_df_copy[final_cols]
    
    # Save to CSV
    output_file = output_dir / 'common_f1_zero_failures.csv'
    common_df_ordered.to_csv(output_file, index=False)
    print(f"📊 Saved common F1=0 failures to: {output_file}")
    
    return common_df_ordered

def main():
    output_dir = 'worst_examples_detailed'
    
    # Load both analyses
    print("📂 Loading analysis data for both models...")
    gpt5_df, gemini_df = load_both_analyses()
    
    # Find common F1=0 questions
    print("🔍 Finding questions where both models had F1=0...")
    common_df, gpt5_zero, gemini_zero = find_common_zero_f1(gpt5_df, gemini_df)
    
    # Analyze patterns
    print("📊 Analyzing common failure patterns...")
    patterns = analyze_common_failure_patterns(common_df)
    
    # Print detailed comparison
    print_detailed_comparison(common_df, patterns, gpt5_zero, gemini_zero)
    
    # Save CSV
    detailed_df = save_common_failures_csv(common_df, output_dir)
    
    # Create plots
    print("📈 Creating comparison plots...")
    create_comparison_plots(common_df, gpt5_zero, gemini_zero, output_dir)
    
    print(f"\n✅ Common failure analysis complete! Check {output_dir}/ for results")

if __name__ == "__main__":
    main() 