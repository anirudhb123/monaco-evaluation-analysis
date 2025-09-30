#!/bin/bash
#
#SBATCH --partition=p_nlp
#SBATCH --job-name=monaco_oracle_gpt5
#SBATCH --output=/mnt/nlpgridio3/data/anirudh2/monaco/logs/monaco_oracle_%j.out
#SBATCH --error=/mnt/nlpgridio3/data/anirudh2/monaco/logs/monaco_oracle_%j.err
#SBATCH --time=08:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4

# MoNaCo Oracle Retrieval Evaluation - SLURM Job
# Submit with: sbatch run_monaco_oracle.sh

echo "🚀 Starting MoNaCo Oracle Retrieval Evaluation on SLURM"
echo "📅 Job started at: $(date)"
echo "🏷️  Job ID: $SLURM_JOB_ID"
echo "🖥️  Node: $SLURMD_NODENAME"

# Configuration - can be set via environment variables or command line arguments
NUM_QUESTIONS=${1:-${NUM_QUESTIONS:-200}}
START_QUESTION=${2:-${START_QUESTION:-0}}
MODEL=${MODEL:-"gemini-2.5-pro"}
MAX_WORKERS=${MAX_WORKERS:-3}
REQUESTS_PER_MINUTE=${REQUESTS_PER_MINUTE:-60}

echo "⚙️  Configuration:"
echo "   Questions: $NUM_QUESTIONS"
echo "   Start from: $START_QUESTION"
echo "   Model: $MODEL"
echo "   Max Workers: $MAX_WORKERS"
echo "   Rate Limit: $REQUESTS_PER_MINUTE req/min"
echo ""

# Create necessary directories
mkdir -p /mnt/nlpgridio3/data/anirudh2/monaco/logs
mkdir -p /mnt/nlpgridio3/data/anirudh2/monaco/results

# Change to the working directory
cd /mnt/nlpgridio3/data/anirudh2/monaco

# Load Python environment (adjust as needed)
module load python/3.9
# If using conda: source activate your_env
# If using venv: source venv/bin/activate

# Install requirements if needed
if [ ! -f "requirements_scalable.txt" ] || ! pip freeze | grep -q "tenacity"; then
    echo "📦 Installing requirements..."
    pip install -r requirements_scalable.txt
fi

# Verify files exist
if [ ! -f "monaco_version_1_release.json" ]; then
    echo "❌ Error: QA file not found"
    exit 1
fi

if [ ! -f "docs_oracle_retrieval_2025.jsonl" ]; then
    echo "❌ Error: Oracle docs file not found"
    exit 1
fi

# Check API keys are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not set"
    exit 1
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Error: GOOGLE_API_KEY not set"
    exit 1
fi

echo "🔑 API key found (length: ${#OPENAI_API_KEY} characters)"

# Generate output files with job ID and timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="results/monaco_oracle_${MODEL}_${NUM_QUESTIONS}q_job${SLURM_JOB_ID}_${TIMESTAMP}.json"
CHECKPOINT_FILE="results/checkpoint_${MODEL}_${NUM_QUESTIONS}q_job${SLURM_JOB_ID}.json"

echo "💾 Output file: $OUTPUT_FILE"
echo "🔄 Checkpoint file: $CHECKPOINT_FILE"
echo ""

# Run the evaluation
echo "🔄 Starting evaluation..."
srun python run_gemini_oracle.py \
    --openai_api_key "$OPENAI_API_KEY" \
    --google_api_key "$GOOGLE_API_KEY" \
    --qa_file "monaco_version_1_release.json" \
    --oracle_docs "docs_oracle_retrieval_2025.jsonl" \
    --output "$OUTPUT_FILE" \
    --checkpoint "$CHECKPOINT_FILE" \
    --model "gemini-2.5-pro" \
    --judge_model "gpt-4.1" \
    --max_questions "$NUM_QUESTIONS" \
    --start_question "$START_QUESTION" \
    --max_workers "$MAX_WORKERS" \
    --requests_per_minute "$REQUESTS_PER_MINUTE" \
    --checkpoint_interval 25

exit_code=$?

echo ""
echo "📅 Job finished at: $(date)"
if [ $exit_code -eq 0 ]; then
    echo "✅ Evaluation completed successfully!"
    echo "📊 Results saved to: $OUTPUT_FILE"
    
    # Clean up checkpoint file on success
    if [ -f "$CHECKPOINT_FILE" ]; then
        rm "$CHECKPOINT_FILE"
        echo "🧹 Checkpoint file cleaned up"
    fi
else
    echo "❌ Evaluation failed with exit code: $exit_code"
    echo "🔄 You can resume using the checkpoint: $CHECKPOINT_FILE"
fi

echo "🏷️  Final Job ID: $SLURM_JOB_ID" 