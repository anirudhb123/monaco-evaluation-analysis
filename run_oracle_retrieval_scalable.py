#!/usr/bin/env python3
"""
MoNaCo Oracle Retrieval Evaluation Script - Scalable Version

This script runs the Oracle retrieval mode for MoNaCo benchmark evaluation
with improvements for large-scale deployment:
- Rate limiting and retry logic
- Checkpointing and resume capability
- Parallel processing
- Memory-efficient streaming
- Better error handling and logging
"""

import os
import sys
import json
import argparse
import time
import logging
from typing import Dict, List, Any, Optional
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import openai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prompts'))

from utils import load_json, write_to_json, write_jsonl
from prompts.retrieval_augmented_setup import get_formatted_gold_documents_list
from prompts.answer_judgement_prompt_V2 import single_answer_llm_judge_prompt, multi_answer_llm_judge_prompt
from prompts.evaluate_final_answers import compute_llm_judge_score_V2


@dataclass
class EvaluationConfig:
    """Configuration for the evaluation run."""
    qa_file: str
    oracle_docs_file: str
    api_key: str
    output_file: str = "oracle_retrieval_results.json"
    checkpoint_file: str = "oracle_checkpoint.json"
    model: str = "gpt-4"
    max_questions: Optional[int] = None
    start_question: int = 0  # Starting question index (0-based)
    max_workers: int = 5  # Number of parallel workers
    requests_per_minute: int = 60  # Rate limit
    checkpoint_interval: int = 10  # Save checkpoint every N processed questions
    max_retries: int = 3
    retry_wait_min: float = 1.0
    retry_wait_max: float = 60.0


def setup_logging(log_file: str = "oracle_evaluation.log"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def setup_openai_client(api_key: str):
    """Initialize OpenAI client with API key."""
    return openai.OpenAI(api_key=api_key)


def create_oracle_retrieval_prompt(question: str, gold_documents: List[str]) -> str:
    """Create a prompt with question and gold documents for Oracle retrieval."""
    documents_text = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(gold_documents)])
    
    prompt = f"""You are given a question and relevant documents. Please answer the question based on the provided documents.

Question: {question}

Relevant Documents:
{documents_text}

Please provide a comprehensive and accurate answer based on the documents provided above. If the question asks for multiple items, list them clearly. Be specific and cite information from the documents when possible.

Answer:"""
    
    return prompt


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.last_request_time = 0.0
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limit."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError))
)
def get_llm_response_with_retry(client: openai.OpenAI, prompt: str, model: str, rate_limiter: RateLimiter) -> str:
    """Get response from LLM with retry logic and rate limiting."""
    rate_limiter.wait_if_needed()
    
    try:
        # Use different parameter names for different models
        if "gpt-5" in model:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
        else:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error getting LLM response: {e}")
        raise


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError))
)
def evaluate_answer_with_retry(client: openai.OpenAI, question: str, response: str, correct_answer: str, 
                              gold_answers_length: int, model: str, rate_limiter: RateLimiter) -> Dict[str, Any]:
    """Evaluate the answer using LLM-as-judge with retry logic."""
    rate_limiter.wait_if_needed()
    
    # Choose the appropriate prompt based on number of answers
    if gold_answers_length == 1:
        judge_prompt = single_answer_llm_judge_prompt.format(
            question=question,
            response=response,
            correct_answer=correct_answer
        )
    else:
        judge_prompt = multi_answer_llm_judge_prompt.format(
            question=question,
            response=response,
            correct_answer=correct_answer
        )
    
    try:
        # Use different parameter names for different models
        if "gpt-5" in model:
            judge_response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": judge_prompt}
                ]
            )
        else:
            judge_response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": judge_prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
        
        judgment = judge_response.choices[0].message.content.strip()
        scores = compute_llm_judge_score_V2(judgment, gold_answers_length)
        
        return {
            "judgment": judgment,
            "scores": scores
        }
    except Exception as e:
        logging.error(f"Error evaluating answer: {e}")
        raise


def process_single_question(question: str, qa_info: Dict, question_docs_map: Dict, 
                          client: openai.OpenAI, config: EvaluationConfig, 
                          rate_limiter: RateLimiter) -> Optional[Dict[str, Any]]:
    """Process a single question and return the result."""
    try:
        # Get formatted gold documents
        gold_documents = get_formatted_gold_documents_list(
            question, question_docs_map, is_bm25_retrieval=False
        )
        
        if not gold_documents:
            logging.warning(f"No valid documents for question: {question[:100]}...")
            return None
        
        # Create Oracle retrieval prompt
        oracle_prompt = create_oracle_retrieval_prompt(question, gold_documents)
        
        # Get LLM response
        llm_response = get_llm_response_with_retry(client, oracle_prompt, config.model, rate_limiter)
        
        if not llm_response:
            logging.warning(f"No LLM response for question: {question[:100]}...")
            return None
        
        # Evaluate the answer
        gold_answers = qa_info.get("validated_answer", qa_info.get("gold_answers", []))
        if isinstance(gold_answers, list) and len(gold_answers) > 0 and isinstance(gold_answers[0], list):
            # Handle nested list format like [['disorder', 'symptom', 'treatment'], ...]
            gold_answers_str = " | ".join([" - ".join(map(str, answer)) for answer in gold_answers])
        else:
            gold_answers_str = " | ".join(map(str, gold_answers)) if isinstance(gold_answers, list) else str(gold_answers)
        
        evaluation = evaluate_answer_with_retry(
            client, question, llm_response, gold_answers_str, 
            len(gold_answers) if isinstance(gold_answers, list) else 1, config.model, rate_limiter
        )
        
        # Store results
        result = {
            "question": question,
            "gold_answers": gold_answers,
            "llm_response": llm_response,
            "evaluation": evaluation,
            "num_gold_documents": len(gold_documents),
            "canary": qa_info.get("canary", "")
        }
        
        return result
        
    except Exception as e:
        logging.error(f"Error processing question {question[:100]}: {e}")
        return None


def save_checkpoint(checkpoint_file: str, processed_questions: List[str], results: List[Dict], 
                   total_score: float, processed_count: int):
    """Save checkpoint data."""
    checkpoint_data = {
        "processed_questions": processed_questions,
        "results": results,
        "total_score": total_score,
        "processed_count": processed_count,
        "timestamp": time.time()
    }
    write_to_json(checkpoint_data, checkpoint_file)
    logging.info(f"Checkpoint saved: {processed_count} questions processed")


def load_checkpoint(checkpoint_file: str) -> Optional[Dict]:
    """Load checkpoint data if it exists."""
    if os.path.exists(checkpoint_file):
        try:
            checkpoint_data = load_json(checkpoint_file)
            logging.info(f"Checkpoint loaded: {checkpoint_data['processed_count']} questions already processed")
            return checkpoint_data
        except Exception as e:
            logging.error(f"Error loading checkpoint: {e}")
    return None


def run_oracle_retrieval_evaluation_scalable(config: EvaluationConfig):
    """Run the complete Oracle retrieval evaluation with scalability improvements."""
    
    logger = setup_logging()
    logger.info("🚀 Starting MoNaCo Oracle Retrieval Evaluation (Scalable Version)")
    logger.info(f"📁 QA File: {config.qa_file}")
    logger.info(f"📁 Oracle Docs File: {config.oracle_docs_file}")
    logger.info(f"🤖 Model: {config.model}")
    logger.info(f"💾 Output File: {config.output_file}")
    logger.info(f"🔄 Max Workers: {config.max_workers}")
    logger.info(f"⏱️  Rate Limit: {config.requests_per_minute} req/min")
    
    # Initialize OpenAI client and rate limiter
    client = setup_openai_client(config.api_key)
    rate_limiter = RateLimiter(config.requests_per_minute)
    
    # Load QA data
    logger.info("📖 Loading QA data...")
    qa_data = load_json(config.qa_file)
    
    # Create question-to-documents mapping from Oracle docs
    logger.info("🗂️  Processing Oracle documents...")
    from prompts.retrieval_augmented_setup import index_gold_documents_by_question
    
    # Create temporary mapping file
    temp_mapping_file = "temp_oracle_mapping.json"
    index_gold_documents_by_question(config.oracle_docs_file, temp_mapping_file)
    question_docs_map = load_json(temp_mapping_file)
    
    # Clean up temp file
    os.remove(temp_mapping_file)
    
    logger.info(f"📊 Found {len(qa_data)} questions in QA file")
    logger.info(f"📊 Found {len(question_docs_map)} questions with Oracle documents")
    
    # Process questions - prioritize questions that have Oracle documents
    all_qa_questions = list(qa_data.keys())
    questions_with_oracle = [q for q in all_qa_questions if q in question_docs_map]
    questions_without_oracle = [q for q in all_qa_questions if q not in question_docs_map]
    
    # Start with questions that have Oracle documents
    questions_to_process = questions_with_oracle + questions_without_oracle
    
    # Apply start_question offset
    if config.start_question > 0:
        questions_to_process = questions_to_process[config.start_question:]
        logger.info(f"🔢 Starting from question index {config.start_question}")
    
    # Apply max_questions limit
    if config.max_questions:
        questions_to_process = questions_to_process[:config.max_questions]
    
    # Load checkpoint if exists
    checkpoint_data = load_checkpoint(config.checkpoint_file)
    if checkpoint_data:
        processed_questions = set(checkpoint_data["processed_questions"])
        results = checkpoint_data["results"]
        total_score = checkpoint_data["total_score"]
        processed_count = checkpoint_data["processed_count"]
        
        # Filter out already processed questions
        questions_to_process = [q for q in questions_to_process if q not in processed_questions]
        logger.info(f"🔄 Resuming from checkpoint. {len(questions_to_process)} questions remaining")
    else:
        processed_questions = set()
        results = []
        total_score = 0.0
        processed_count = 0
    
    logger.info(f"🔄 Processing {len(questions_to_process)} questions...")
    
    # Process questions in parallel batches
    batch_size = config.max_workers * 2  # Process in small batches to allow for checkpointing
    
    # Initialize progress bar for SLURM (with explicit flush)
    progress_bar = tqdm(
        total=len(questions_to_process), 
        desc="Processing questions", 
        unit="q",
        mininterval=1.0,  # Update every second
        file=sys.stdout
    )
    
    for i in range(0, len(questions_to_process), batch_size):
        batch_questions = questions_to_process[i:i+batch_size]
        
        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            # Submit tasks for this batch
            future_to_question = {}
            for question in batch_questions:
                if question not in question_docs_map:
                    continue
                    
                qa_info = qa_data[question]
                future = executor.submit(
                    process_single_question, 
                    question, qa_info, question_docs_map, 
                    client, config, rate_limiter
                )
                future_to_question[future] = question
            
            # Process completed tasks
            for future in as_completed(future_to_question):
                question = future_to_question[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        total_score += result["evaluation"]["scores"]["judge_score"]
                        processed_count += 1
                        processed_questions.add(question)
                        
                        # Update progress bar (only every few completions to reduce noise)
                        avg_score = total_score / processed_count
                        if processed_count % 1 == 0:  # Update on every completion but less noisy
                            progress_bar.set_postfix({
                                'avg_score': f'{avg_score:.3f}',
                                'score': f'{result["evaluation"]["scores"]["judge_score"]:.2f}'
                            })
                            progress_bar.update(1)
                        
                        # Save checkpoint periodically
                        if processed_count % config.checkpoint_interval == 0:
                            save_checkpoint(
                                config.checkpoint_file, 
                                list(processed_questions), 
                                results, 
                                total_score, 
                                processed_count
                            )
                
                except Exception as e:
                    logger.error(f"Error processing question {question[:100]}: {e}")
                    progress_bar.update(1)  # Still update progress on error
    
    progress_bar.close()
    
    # Calculate final metrics
    if processed_count > 0:
        final_avg_score = total_score / processed_count
        logger.info(f"\n🎯 Final Results:")
        logger.info(f"📊 Total Questions Processed: {processed_count}")
        logger.info(f"🏆 Average Judge Score: {final_avg_score:.3f}")
        
        # Save detailed results
        output_data = {
            "metadata": {
                "total_questions": len(questions_to_process) + processed_count - len(results),
                "processed_questions": processed_count,
                "average_judge_score": final_avg_score,
                "model": config.model,
                "qa_file": config.qa_file,
                "oracle_docs_file": config.oracle_docs_file,
                "max_workers": config.max_workers,
                "requests_per_minute": config.requests_per_minute
            },
            "results": results
        }
        
        write_to_json(output_data, config.output_file)
        logger.info(f"💾 Results saved to: {config.output_file}")
        
        # Clean up checkpoint file
        if os.path.exists(config.checkpoint_file):
            os.remove(config.checkpoint_file)
            logger.info("🧹 Checkpoint file cleaned up")
        
        return output_data
    else:
        logger.error("❌ No questions were successfully processed!")
        return None


def main():
    parser = argparse.ArgumentParser(description="Run MoNaCo Oracle Retrieval Evaluation (Scalable Version)")
    parser.add_argument("--api_key", required=True, help="OpenAI API key")
    parser.add_argument("--qa_file", default="monaco_version_1_release.json", 
                       help="Path to QA file with gold answers")
    parser.add_argument("--oracle_docs", default="docs_oracle_retrieval_2025.jsonl",
                       help="Path to Oracle retrieval documents file")
    parser.add_argument("--output", default="oracle_retrieval_results.json",
                       help="Output file for results")
    parser.add_argument("--checkpoint", default="oracle_checkpoint.json",
                       help="Checkpoint file for resume capability")
    parser.add_argument("--model", default="gpt-4", 
                       help="OpenAI model to use (gpt-4, gpt-4-turbo, etc.)")
    parser.add_argument("--max_questions", type=int, default=None,
                       help="Maximum number of questions to process (for testing)")
    parser.add_argument("--start_question", type=int, default=0,
                       help="Starting question index (0-based, default: 0)")
    parser.add_argument("--max_workers", type=int, default=5,
                       help="Number of parallel workers (default: 5)")
    parser.add_argument("--requests_per_minute", type=int, default=60,
                       help="Rate limit for API calls (default: 60)")
    parser.add_argument("--checkpoint_interval", type=int, default=10,
                       help="Save checkpoint every N questions (default: 10)")
    
    args = parser.parse_args()
    
    # Validate files exist
    if not os.path.exists(args.qa_file):
        print(f"❌ QA file not found: {args.qa_file}")
        sys.exit(1)
        
    if not os.path.exists(args.oracle_docs):
        print(f"❌ Oracle docs file not found: {args.oracle_docs}")
        sys.exit(1)
    
    # Create configuration
    config = EvaluationConfig(
        qa_file=args.qa_file,
        oracle_docs_file=args.oracle_docs,
        api_key=args.api_key,
        output_file=args.output,
        checkpoint_file=args.checkpoint,
        model=args.model,
        max_questions=args.max_questions,
        start_question=args.start_question,
        max_workers=args.max_workers,
        requests_per_minute=args.requests_per_minute,
        checkpoint_interval=args.checkpoint_interval
    )
    
    # Run evaluation
    run_oracle_retrieval_evaluation_scalable(config)


if __name__ == "__main__":
    main() 