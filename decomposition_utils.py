import csv

from utils import read_csv_to_dict, remove_empty_string_from_list, remove_duplicates_from_list

REF = "#"
LIST_STEP_IDENTIFIER = "[list]"


def is_step_dependent_on_other(step_idx, depend_on_idx, decomposition_list):

    def all_dependent_steps(steps, idx):
        step = steps[idx - 1]
        dependent_indices = extract_references(step)
        if not dependent_indices:
            return dependent_indices
        else:
            for ref in dependent_indices:
                dependent_indices += all_dependent_steps(steps, ref)
            return remove_duplicates_from_list(dependent_indices)

    return depend_on_idx in all_dependent_steps(decomposition_list, step_idx)


def steps_are_column_attributes(decomposition_list, target_steps_indices):
    """given two decomposition steps, we regard them as column attributed if they all refer to one of the input steps
    or if all refer to the same previous step."""

    def all_steps_refer_to_target(target_step_idx, other_steps):
        for other in other_steps:
            if target_step_idx not in step_to_references_map[other]:
                return False
        return True

    def all_steps_depend_on_target(target_step_idx, other_steps):
        for other in other_steps:
            if not is_step_dependent_on_other(other, target_step_idx, decomposition_list):
                return False
        return True

    step_to_references_map = {}
    for index in target_steps_indices:
        step_to_references_map[index] = extract_references(decomposition_list[index - 1])
    for index in range(1, len(decomposition_list) + 1):
        # check if all target steps refer to one single step (potentially one of them)
        steps_excluding_idx = [x for x in target_steps_indices if x != index]
        if all_steps_refer_to_target(index, steps_excluding_idx) or \
                all_steps_depend_on_target(index, steps_excluding_idx):
            return True
    return False


def remove_list_step_identifier(qdmr_step):
    return qdmr_step.replace(LIST_STEP_IDENTIFIER, "").strip()


def decomposition_to_steps(decomposition):
    """QDMR format example:
        1. Which years did Serena Williams win the Australian open?
        2. return highest of #1
        3. return difference of 2022 and #2"""

    def no_number_prefix(step_str):
        return ' '.join(step_str.split(". ")[1:]).strip()

    dec_steps = decomposition.split("\n")
    dec_steps = [no_number_prefix(step) for step in dec_steps]
    return remove_empty_string_from_list(dec_steps)


def is_base_question(decomposition_step, step_no):
    """does the question contain a reference"""
    if decomposition_step.startswith("return ### "):
        return False
    for i in range(step_no):
        if f"{REF}{i + 1} " in decomposition_step or f" {REF}{i + 1}" in decomposition_step:
            return False
    return True


def is_discrete_qdmr_step(qdmr_step):
    """determine whether qdmr step represents a discrete operation: count, comparison, group
    or does it represent a question to be manually annotated"""
    return qdmr_step.lower().startswith("return ")


def extract_references(qdmr_step):
    """Extracts a list of references to previous steps"""
    # make sure decomposition does not contain a mere '# ' other than a reference.
    qdmr_step = qdmr_step.replace("# ", "hashtag ").replace(",", "").replace("?", "").replace(";", "").replace(")",
                                                                                                               "").replace(
        "(", "")
    references = []
    l = qdmr_step.split(REF)
    for chunk in l[1:]:
        if len(chunk) > 1:
            ref = chunk.split()[0].replace("'s", "")
            ref = int(ref)
            references += [ref]
        if len(chunk) == 1:
            ref = int(chunk)
            references += [ref]
    return references


def populate_qdmr_step(qdmr_step, assignment):
    ref_idxs = extract_references(qdmr_step)
    populated_step = qdmr_step
    for ref in [str(r) for r in ref_idxs]:
        if assignment[ref] is None:
            assignment[ref] = "None"
        populated_step = populated_step.replace(f"{REF}{ref}", str(assignment[ref]))
    return populated_step


def is_reference_token(tok):
    if tok.startswith(REF) and len(tok) <= 3:
        return True


def identify_populated_step_idx(populated_step, decomposition_list):
    def non_ref_tokens_contained(qdmr_step, populated_step):
        tokens = qdmr_step.split()
        populated_step_tokens = populated_step.split()
        for tok in tokens:
            if tok not in populated_step_tokens and not is_reference_token(tok):
                return False
        return True

    for i in range(len(decomposition_list)):
        decomposition_step = remove_list_step_identifier(decomposition_list[i])
        if non_ref_tokens_contained(decomposition_step, populated_step):
            return i + 1
    return None


def extract_base_set_questions(qdmr_csv, output_csv):
    """
    Given a QDMR as input, extract its base questions (select steps).
    input csv headers are: question, decomposition, question_origin
    """

    def get_base_questions(decomposition):
        steps = decomposition_to_steps(decomposition)
        return list(filter(lambda x: is_base_question(x, len(steps)), steps))

    data = read_csv_to_dict(qdmr_csv, encoding='latin1')
    output = []
    for example in data:
        base_questions = get_base_questions(example['decomposition'])
        full_q = example['question']
        for base_q in base_questions:
            output += [{'base_question': base_q, 'original_question': full_q}]
    # write data to new csv
    csv_columns = ['base_question', 'original_question']
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for ex in output:
            writer.writerow(ex)
    return True
