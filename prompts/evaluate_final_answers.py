def compute_llm_judge_score_V2(llm_judgement, gold_answers_length):
    def extract_single_answer_score():
        try:
            prec = float(llm_judgement.split("final precision:")[1].split("\n")[0].replace("...", ""))
        except ValueError:
            prec = 0.0
        return {"judge_score": prec, "precision": prec}

    def extract_multi_answer_scores():
        length_keyword = "\nfinal answer length:"
        if length_keyword not in llm_judgement:
            return None
        len_substr = llm_judgement.replace("final answer length: None ", "final answer length: 0 ")
        len_substr = len_substr.replace("The response lists over", "")
        len_substr = len_substr.split(length_keyword)[1].strip().split("\n")[0].strip()
        len_substr = len_substr.split(" ")[0].strip() if " " in len_substr else len_substr
        predicted_length = int(len_substr)
        correct_predicted_answers_keyword = "\noverlapping answers:"
        if correct_predicted_answers_keyword not in llm_judgement:
            return None
        answer_delimiter = "###"
        empty_answer_keyword = "NULL"
        answers_chunk = llm_judgement.split(correct_predicted_answers_keyword)[1].replace(
            answer_delimiter + empty_answer_keyword, answer_delimiter).strip()
        answers_chunk = answers_chunk[:-3] if answers_chunk.endswith(answer_delimiter) else answers_chunk
        answers = answers_chunk.split(answer_delimiter)
        num_correct = len(answers) if answers != [empty_answer_keyword] else 0
        if predicted_length == 0.0:
            recall = 0.0
            precision = 0.0
            f1 = 0.0
        else:
            recall = float(min(num_correct, gold_answers_length)) / gold_answers_length if num_correct != 0 else 0.0
            predicted_length = max(predicted_length, num_correct)  # accounts for potential errors in LLM generation
            precision = float(num_correct) / predicted_length if num_correct != 0 else 0.0
            f1 = (2 * (precision * recall)) / (precision + recall) if num_correct != 0 else 0.0
        return {"judge_score": f1, "precision": precision, "recall": recall, "gold answers length": gold_answers_length,
                "predicted answers num": predicted_length, "correct predictions": answers, "num correct": num_correct}

    llm_judgement = llm_judgement.replace("final_answer_length", "final answer length")
    llm_judgement = llm_judgement.replace("overlapping_answers", "overlapping answers")
    llm_judgement = llm_judgement.replace("final_precision", "final precision")
    if gold_answers_length == 1:
        return extract_single_answer_score()
    if gold_answers_length > 1:
        return extract_multi_answer_scores()
    raise Exception
