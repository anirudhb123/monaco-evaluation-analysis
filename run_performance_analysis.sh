#!/bin/bash

# MoNaCo LLM Performance Breakdown Analysis Runner
# Submit to SLURM for analysis

if [ $# -eq 0 ]; then
    echo "Usage: ./run_performance_analysis.sh <results_file>"
    echo "Example: ./run_performance_analysis.sh merged_results/monaco_results_gpt4_judge.json"
    exit 1
fi

echo "🚀 Submitting MoNaCo analysis to SLURM..."
echo "Analyzing file: $1"

sbatch --job-name="monaco_analysis_$(basename $1)" \
       --output="logs/monaco_analysis_%j.out" \
       --error="logs/monaco_analysis_%j.err" \
       --time=01:00:00 \
       --nodes=1 \
       --ntasks=1 \
       --cpus-per-task=4 \
       --mem=16G \
       --partition=p_nlp \
       --wrap="cd /mnt/nlpgridio3/data/anirudh2/monaco && mkdir -p logs performance_analysis_results performance_analysis_plots && pip install --user -r requirements_analysis.txt && python llm_performance_breakdown.py $1"

echo "📋 Job submitted! Check status with: squeue -u $USER"
echo "📁 Results will be saved in performance_analysis_results/ and performance_analysis_plots/" 