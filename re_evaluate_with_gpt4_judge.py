#!/usr/bin/env python3
"""
Re-evaluate Monaco results using GPT-4.1 as judge instead of GPT-5.
This script takes existing GPT-5 responses and re-scores them with an external judge.
"""

import json
import os
import sys
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

from prompts.answer_judgement_prompt_V2 import single_answer_llm_judge_prompt, multi_answer_llm_judge_prompt
from prompts.evaluate_final_answers import compute_llm_judge_score_V2

@dataclass
class ReEvaluationConfig:
    """Configuration for the re-evaluation run."""
    input_file: str
    output_file: str
    api_key: str
    judge_model: str = "gpt-4.1"  # GPT-4.1 model
    max_workers: int = 3
    requests_per_minute: int = 60
    checkpoint_interval: int = 25
    max_retries: int = 3

class RateLimiter:
    """Simple rate limiter for API calls."""
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.last_request_time = 0
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limit."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_interval:
            time.sleep(self.min_interval - time_since_last)
        self.last_request_time = time.time()

def setup_logging() -> logging.Logger:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('re_evaluation.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def setup_openai_client(api_key: str):
    """Initialize OpenAI client with API key."""
    return openai.OpenAI(api_key=api_key)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError))
)
def evaluate_answer_with_gpt4_judge(client: openai.OpenAI, question: str, response: str, 
                                  correct_answer: str, gold_answers_length: int, 
                                  judge_model: str, rate_limiter: RateLimiter) -> Dict[str, Any]:
    """Evaluate the answer using GPT-4.1 as judge with retry logic."""
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
        # Use GPT-4.1 for judging
        judge_response = client.chat.completions.create(
            model=judge_model,
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
            "scores": scores,
            "judge_model": judge_model
        }
    
    except Exception as e:
        logging.error(f"Error evaluating answer with GPT-4 judge: {e}")
        raise

def process_single_result(result: Dict[str, Any], client: openai.OpenAI, 
                         config: ReEvaluationConfig, rate_limiter: RateLimiter) -> Dict[str, Any]:
    """Re-evaluate a single result with GPT-4.1 judge."""
    try:
        question = result["question"]
        llm_response = result["llm_response"]
        gold_answers = result["gold_answers"]
        
        # Format gold answers for evaluation
        if isinstance(gold_answers, list) and len(gold_answers) > 0 and isinstance(gold_answers[0], list):
            # Handle nested list format
            gold_answers_str = " | ".join([" - ".join(map(str, answer)) for answer in gold_answers])
        else:
            gold_answers_str = " | ".join(map(str, gold_answers)) if isinstance(gold_answers, list) else str(gold_answers)
        
        # Get new evaluation with GPT-4.1 judge
        new_evaluation = evaluate_answer_with_gpt4_judge(
            client, question, llm_response, gold_answers_str,
            len(gold_answers) if isinstance(gold_answers, list) else 1,
            config.judge_model, rate_limiter
        )
        
        # Create new result with both evaluations
        new_result = result.copy()
        new_result["original_evaluation"] = result["evaluation"]  # Keep original GPT-5 evaluation
        new_result["evaluation"] = new_evaluation  # Replace with GPT-4.1 evaluation
        new_result["judge_model_used"] = config.judge_model
        
        return new_result
    
    except Exception as e:
        logging.error(f"Error processing result for question: {result.get('question', 'unknown')[:100]}...")
        logging.error(f"Error: {e}")
        return None

def load_existing_results(input_file: str) -> Dict[str, Any]:
    """Load existing Monaco results."""
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_results(results: List[Dict[str, Any]], metadata: Dict[str, Any], output_file: str):
    """Save re-evaluated results."""
    output_data = {
        "metadata": metadata,
        "results": results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

def create_comparison_report(original_data: Dict[str, Any], new_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a comparison report between GPT-5 and GPT-4.1 judging."""
    original_scores = [r["evaluation"]["scores"]["judge_score"] for r in original_data["results"]]
    
    # Extract valid new scores
    new_scores = []
    for r in new_results:
        if (r is not None and r.get("evaluation") and r["evaluation"].get("scores") 
            and r["evaluation"]["scores"].get("judge_score") is not None):
            new_scores.append(r["evaluation"]["scores"]["judge_score"])
    
    # Calculate metrics
    original_avg = sum(original_scores) / len(original_scores)
    new_avg = sum(new_scores) / len(new_scores) if new_scores else 0
    
    # Score differences for matched questions
    score_diffs = []
    for i, new_result in enumerate(new_results):
        if (new_result is not None and new_result.get("evaluation") and 
            new_result["evaluation"].get("scores") and 
            new_result["evaluation"]["scores"].get("judge_score") is not None):
            orig_score = original_data["results"][i]["evaluation"]["scores"]["judge_score"]
            new_score = new_result["evaluation"]["scores"]["judge_score"]
            score_diffs.append(new_score - orig_score)
    
    return {
        "comparison_summary": {
            "total_questions": len(original_scores),
            "successfully_re_evaluated": len(new_scores),
            "gpt5_judge_average": original_avg,
            "gpt41_judge_average": new_avg,
            "average_score_difference": sum(score_diffs) / len(score_diffs) if score_diffs else 0,
            "gpt41_vs_gpt5_improvement": new_avg - original_avg,
            "questions_scored_higher_by_gpt41": sum(1 for diff in score_diffs if diff > 0.01),
            "questions_scored_lower_by_gpt41": sum(1 for diff in score_diffs if diff < -0.01),
            "questions_scored_similar": sum(1 for diff in score_diffs if abs(diff) <= 0.01)
        },
        "score_differences": score_diffs
    }

def main():
    """Main function to run the re-evaluation."""
    logger = setup_logging()
    
    # Configuration
    config = ReEvaluationConfig(
        input_file="merged_results/merged_monaco_results.json",
        output_file="merged_results/monaco_results_gpt4_judge.json",
        api_key=os.getenv("OPENAI_API_KEY"),
        judge_model="gpt-4.1",  # Use GPT-4.1 as judge
        max_workers=3,
        requests_per_minute=60
    )
    
    if not config.api_key:
        logger.error("❌ OPENAI_API_KEY environment variable not set")
        return
    
    logger.info("🔄 Starting Monaco Re-evaluation with GPT-4.1 Judge")
    logger.info(f"📁 Input file: {config.input_file}")
    logger.info(f"📁 Output file: {config.output_file}")
    logger.info(f"🤖 Judge model: {config.judge_model}")
    logger.info(f"🔄 Max workers: {config.max_workers}")
    logger.info(f"⏱️  Rate limit: {config.requests_per_minute} req/min")
    
    # Load existing results
    logger.info("📖 Loading existing results...")
    try:
        original_data = load_existing_results(config.input_file)
        original_results = original_data["results"]
        logger.info(f"✅ Loaded {len(original_results)} existing results")
    except Exception as e:
        logger.error(f"❌ Error loading existing results: {e}")
        return
    
    # Initialize OpenAI client and rate limiter
    client = setup_openai_client(config.api_key)
    rate_limiter = RateLimiter(config.requests_per_minute)
    
    # Re-evaluate all results
    logger.info("🔄 Starting re-evaluation with GPT-4.1 judge...")
    new_results = []
    
    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        # Submit all tasks
        future_to_index = {}
        for i, result in enumerate(original_results):
            future = executor.submit(
                process_single_result,
                result, client, config, rate_limiter
            )
            future_to_index[future] = i
        
        # Process completed tasks with progress bar
        with tqdm(total=len(original_results), desc="Re-evaluating") as pbar:
            completed_results = [None] * len(original_results)  # Maintain order
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    completed_results[index] = result
                    if result:
                        new_results.append(result)
                    pbar.update(1)
                except Exception as e:
                    logger.error(f"Error processing result {index}: {e}")
                    pbar.update(1)
    
    # Update metadata
    new_metadata = original_data["metadata"].copy()
    new_metadata["re_evaluation_info"] = {
        "original_judge_model": "gpt-5", 
        "new_judge_model": config.judge_model,
        "re_evaluated_questions": len(new_results),
        "original_total_questions": len(original_results),
        "re_evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Recalculate average judge score
    if new_results:
        valid_scores = []
        for r in new_results:
            if r.get("evaluation") and r["evaluation"].get("scores") and r["evaluation"]["scores"].get("judge_score") is not None:
                valid_scores.append(r["evaluation"]["scores"]["judge_score"])
        
        if valid_scores:
            new_avg_score = sum(valid_scores) / len(valid_scores)
            new_metadata["average_judge_score"] = new_avg_score
        new_metadata["processed_questions"] = len(new_results)
        new_metadata["successfully_scored_questions"] = len(valid_scores)
    
    # Save results
    logger.info("💾 Saving re-evaluated results...")
    save_results(completed_results, new_metadata, config.output_file)
    
    # Create comparison report
    logger.info("📊 Creating comparison report...")
    comparison = create_comparison_report(original_data, completed_results)
    
    # Save comparison report
    comparison_file = config.output_file.replace('.json', '_comparison.json')
    with open(comparison_file, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    # Print summary
    logger.info("🎯 Re-evaluation Summary:")
    logger.info(f"📊 Original average (GPT-5 judge): {comparison['comparison_summary']['gpt5_judge_average']:.4f}")
    logger.info(f"📊 New average (GPT-4.1 judge): {comparison['comparison_summary']['gpt41_judge_average']:.4f}")
    logger.info(f"📈 Difference: {comparison['comparison_summary']['gpt41_vs_gpt5_improvement']:+.4f}")
    logger.info(f"📊 GPT-4.1 scored higher: {comparison['comparison_summary']['questions_scored_higher_by_gpt41']}")
    logger.info(f"📊 GPT-4.1 scored lower: {comparison['comparison_summary']['questions_scored_lower_by_gpt41']}")
    logger.info(f"📊 Similar scores: {comparison['comparison_summary']['questions_scored_similar']}")
    
    logger.info(f"✅ Re-evaluation complete!")
    logger.info(f"💾 Results saved to: {config.output_file}")
    logger.info(f"📊 Comparison saved to: {comparison_file}")

if __name__ == "__main__":
    main() 