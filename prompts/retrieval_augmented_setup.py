from utils import read_jsonl, write_to_json, remove_duplicates_from_list, load_json
from tqdm import tqdm


def index_gold_documents_by_question(gold_docs_json, output_json_path):
    """re-format the annotated Wikipedia evidence into a question-to-evidence map format"""
    question_docs_map = {}
    
    # Try to load as regular JSON first, then fall back to JSONL
    try:
        data = load_json(gold_docs_json)
        if isinstance(data, dict):
            # If it's already a dict mapping questions to documents, use it directly
            question_docs_map = data
        else:
            # If it's a list, process each item
            for ex in tqdm(data):
                question_docs_map[ex["question_text"]] = ex["contexts"]
    except:
        # Fall back to JSONL format
        data = read_jsonl(gold_docs_json)
        for ex in tqdm(data):
            question_docs_map[ex["question_text"]] = ex["contexts"]
    
    write_to_json(question_docs_map, output_json_path)
    print(f"* Wrote {len(question_docs_map)} question - gold documents examples to: {output_json_path}")
    return True


def index_bm25_documents_by_question(retrieved_evidence_json, output_json_path):
    """re-format the BM25-retrieved Wikipedia evidence into a question-to-evidence map format"""
    question_docs_map = {}
    data = read_jsonl(retrieved_evidence_json)
    for ex in tqdm(data):
        question_docs_map[ex["question_text"]] = ex["retrieval"]
    write_to_json(question_docs_map, output_json_path)
    print(f"* Wrote {len(question_docs_map)} question - BM25 retrieved documents examples to: {output_json_path}")
    return True


def get_formatted_gold_documents_list(question_text, question_evidence_dict, is_bm25_retrieval=None):
    if question_text not in question_evidence_dict:
        return None
    relevant_documents = question_evidence_dict[question_text]
    formatted_docs = []
    for doc in relevant_documents:
        if is_bm25_retrieval is True:
            section_path = doc['section_path']
            doc_contents = doc['paragraph_text'].replace(section_path, "").replace(":::\n\n", "").strip()
            doc_string = f"*** Document title: {section_path}\n*** Document contents:\n{doc_contents}"
            formatted_docs += [doc_string]
            continue
        if len(doc['text'].lower().strip()) == 0:
            continue
        doc_string = f"*** Document title: {doc['section_path']}\n*** Document contents:\n{doc['text']}"
        formatted_docs += [doc_string]
    formatted_docs = remove_duplicates_from_list(formatted_docs)
    # for doc_str in formatted_docs:
    #     print("*******************")
    #     print(doc_str)
    #     print("*******************")
    return formatted_docs


# index_gold_documents_by_question(gold_docs_json="../data/retrieval_documents/multi_step_rc_gold_docs_all_2025.jsonl",
#                                  output_json_path="../data/retrieval_documents/docs_oracle_retrieval_2025.jsonl")
# index_bm25_documents_by_question(retrieved_evidence_json="../data/retrieval_documents/multi_step_retrieved_bm25_docs.jsonl",
#                                  output_json_path="../data/retrieval_documents/docs_bm25_retrieval_2025.jsonl")

# get_formatted_gold_documents_list(question_text="Which religious faction holds the most seats in the Lebanese parliament, based on the religious affiliation of each political party?",
#                                   question_evidence_dict=load_json("../data/retrieval_documents/docs_bm25_retrieval_2025.jsonl"),
#                                   is_bm25_retrieval=True)