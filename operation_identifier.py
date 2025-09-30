import re

from consts import COMPARISON_OPS, SUPERLATIVE_OPS, ARITHMETIC_OPS, AGGREGATE_OPS, COMPARISON_STEP_OPS
from decomposition_utils import decomposition_to_steps, extract_references
from utils import remove_duplicates_from_list

OP_FILTER_BOOLEAN = "filter_boolean"
OP_FILTER_COMPARE = "filter_compare"
OP_FILTER_VALUE = "filter_value"
OP_FILTER_SUPERLATIVE = "filter_superlative"
OP_ARITHMETIC = "arithmetic"
OP_AGGREGATE = "aggregate"
OP_GROUP = "group"
OP_INTERSECT = "intersect"
OP_DISCARD_LIST = "discard_list"
OP_DISCARD_VALUE = "discard_value"
OP_COMPARISON_NUM = "comparison_num"
OP_COMPARISON_BOOLEAN = "comparison_boolean"
OP_BOOLEAN_AND = "boolean_and"
OP_BOOLEAN_COMPARE = "boolean_compare"
OP_UNION = "union"
OP_SORT = "sort"
OP_TOP_K = "top_k"
OP_K_ITEM = "k_item"


def identify_operation(step_text):
    step_text = step_text.lower().strip()
    if is_filter_boolean(step_text):
        return OP_FILTER_BOOLEAN
    if is_filter_compare(step_text):
        return OP_FILTER_COMPARE
    if is_filter_value(step_text):
        return OP_FILTER_VALUE
    if is_filter_superlative(step_text):
        return OP_FILTER_SUPERLATIVE
    if is_arithmetic(step_text):
        return OP_ARITHMETIC
    if is_aggregate(step_text):
        return OP_AGGREGATE
    if is_group(step_text):
        return OP_GROUP
    if is_intersection(step_text):
        return OP_INTERSECT
    if is_discard_list(step_text):
        return OP_DISCARD_LIST
    if is_discard_value(step_text):
        return OP_DISCARD_VALUE
    if is_comparison_step(step_text):
        if is_comparison_boolean(step_text):
            return OP_COMPARISON_BOOLEAN
        return OP_COMPARISON_NUM
    if is_boolean_and(step_text):
        return OP_BOOLEAN_AND
    if is_boolean_compare(step_text):
        return OP_BOOLEAN_COMPARE
    if is_union(step_text):
        return OP_UNION
    if is_sort(step_text):
        return OP_SORT
    if is_top_k(step_text):
        return OP_TOP_K
    if is_k_item(step_text):
        return OP_K_ITEM
    return None


def is_filter_boolean(step):
    """return #x where #y is true/false"""
    res = re.search("return #[1-9][0-9]? where #[1-9][0-9]? is (true|false)$", step.strip())
    if res is None:
        return False
    return True


def is_filter_superlative(step):
    """return #x where #y is {superlative}"""
    all_ops = "|".join(SUPERLATIVE_OPS)
    superlative_op = f"({all_ops})"
    res = re.search(f"return #[1-9][0-9]? where #[1-9][0-9]? is {superlative_op}$", step.strip())
    return res is not None


def is_filter_compare(step):
    """return #x where #y {comparator} {val}"""
    all_ops = " | ".join(COMPARISON_OPS)
    comparison_op = f"( {all_ops} )"
    pattern = f"return #[1-9][0-9]? where #[1-9][0-9]? [is]*{comparison_op}"
    res = re.search(pattern, step)
    return res is not None


def is_filter_value(step):
    """return #x where #y is {val}"""
    if is_filter_boolean(step) or is_filter_compare(step) or is_filter_superlative(step):
        return False
    res = re.search("return #[1-9][0-9]? where #[1-9][0-9]? is ", step)
    return res is not None


def is_arithmetic(step):
    """return {the / } {arithmetic} of #x and #y"""
    # todo: handle arithmetic combined with group syntax, e.g. 'return difference of #1 and #2 for each #4'
    all_ops = "|".join(ARITHMETIC_OPS)
    arithmetic_op = f"({all_ops})"
    # both arithmetic arguments are references
    pattern = f"[return] [the ]?{arithmetic_op} of #[1-9][0-9]? and #[1-9][0-9]?$"
    res = re.search(pattern, step.strip())
    # first argument is a reference, second argument is number
    pattern_first_ref = f"[return] [the ]?{arithmetic_op} of #[1-9][0-9]? and [0-9]*$"
    res_first_ref = re.search(pattern_first_ref, step.strip())
    # second argument is a reference, first argument is number
    pattern_second_ref = f"[return] [the ]?{arithmetic_op} of [0-9]* and #[1-9][0-9]?$"
    res_second_ref = re.search(pattern_second_ref, step.strip())
    return res is not None or res_first_ref is not None or res_second_ref is not None


def is_aggregate(step):
    """return {the / } {aggregate} of #x"""
    if is_arithmetic(step):
        return False
    all_ops = "|".join(AGGREGATE_OPS)
    aggregate_op = f"({all_ops})"
    pattern = f"[return] [the ]?{aggregate_op} of #[1-9][0-9]?$"
    res = re.search(pattern, step.strip())
    if res is not None:
        return True
    pattern = f"[return] [the ]?different #[1-9][0-9]?$"
    res = re.search(pattern, step.strip())
    return res is not None


def is_group(step):
    all_ops = "|".join(AGGREGATE_OPS)
    aggregate_op = f"({all_ops})"
    pattern = f"[return] [the ]?{aggregate_op} of #[1-9][0-9]? for each #[1-9][0-9]?$"
    res = re.search(pattern, step.strip())
    return res is not None


def is_intersection(step):
    pattern = f"[return] [\s\S]+ in both #[1-9][0-9]? and #[1-9][0-9]?$"
    res = re.search(pattern, step.strip())
    return res is not None


def is_discard_list(step):
    pattern = f"[return] #[1-9][0-9]? besides #[1-9][0-9]?$"
    res = re.search(pattern, step.strip())
    return res is not None


def is_discard_value(step):
    if is_discard_list(step):
        return False
    pattern = f"[return] #[1-9][0-9]? besides [\s\S]+$"
    res = re.search(pattern, step.strip())
    return res is not None


def is_comparison_step(step):
    """return which is {superlative} of #x, #y, ..."""
    all_ops = "|".join(COMPARISON_STEP_OPS)
    comparison_step_op = f"({all_ops})"
    step = step.replace(" ,", ",").strip()
    res = re.search(f"return which is {comparison_step_op} of [#[1-9][0-9]?, #[1-9][0-9]?", step)
    return res is not None


def is_comparison_boolean(step):
    return is_comparison_step(step) and ("which is true of " in step or "which is false of " in step)


def is_sort(step):
    pattern = f"[return] #[1-9][0-9]? (sorted by|ordered by) (#[1-9][0-9]?)*"
    res = re.search(pattern, step.strip())
    return res is not None


def is_top_k(step):
    """return {the / } {top-k} of #x"""
    pattern = f"[return] [ the]?top [\s\S]+ of #[1-9][0-9]?$"
    res = re.search(pattern, step.strip())
    return res is not None


def is_k_item(step):
    """return {the / } {k’th} of #x"""
    all_ops = "|".join(["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"])
    comparison_step_op = f"({all_ops})"
    pattern = f"[return] [the ]?{comparison_step_op} of #[1-9][0-9]?$"
    res = re.search(pattern, step.strip())
    return res is not None


def is_boolean_compare(step):
    """
    return if #x {comparator} {val}
    return if #x {comparator} #y"""
    all_ops = " | ".join(COMPARISON_OPS)
    comparison_op = f"( {all_ops} )"
    pattern = f"return if #[1-9][0-9]? is{comparison_op}"
    res = re.search(pattern, step)
    return res is not None


def is_boolean_and(step):
    """return if both #x and #y are {true / false}"""
    pattern = f"return if both #[1-9][0-9]? and #[1-9][0-9]? are (true|false)$"
    res = re.search(pattern, step.strip())
    return res is not None


def is_union(step):
    """return #x, #y {, #z, …}"""
    norm_step = step.replace("  ", " ").replace(" , ", ", ").replace(",#", ", #").strip()
    pattern = f"return #[1-9][0-9]?, (#[1-9][0-9]?, )*#[1-9][0-9]?$"
    res = re.search(pattern, norm_step.strip())
    return res is not None


def is_valid_qdmr(qdmr_string):
    """validate the input QDMR following these criteria:
        1. Each step is valid QDMR operation
        2. There are no duplicate steps
        3. No step refers to itself or to future steps
        4. Steps that are not used in the decomposition"""

    def is_valid_op(step):
        return identify_operation(step) is not None

    def no_dup_steps():
        norm_steps = [s.lower().strip() for s in steps]
        if len(norm_steps) == len(remove_duplicates_from_list(norm_steps)):
            return True
        print("* Duplicate steps")
        return False

    def no_future_refs():
        for i in range(len(steps)):
            step_i_refs = extract_references(steps[i])
            # try:
            #     step_i_refs = extract_references(steps[i])
            # except ValueError:
            #     print(f"Error in extracting refs from step: {steps[i]} in decomposition:\n{qdmr_string}")
            #     raise ValueError
            for ref in step_i_refs:
                if ref >= i+1:  # no step refers to itself or to future steps
                    print(f"* Future ref: #{ref}")
                    return False
        return True

    def unused_steps():
        for i in range(len(steps)-1):
            idx = i + 1
            if f"#{idx}" not in qdmr_string:
                print(f"* Unused step: {idx}")
                return False
        return True

    steps = decomposition_to_steps(qdmr_string)
    new_steps = []
    for s in steps:
        if len(s.strip()) > 0:  # remove empty steps
            new_steps += [s]
    steps = new_steps
    for s in steps:
        if not is_valid_op(s) and s.startswith("return "):  # discrete step with invalid op
            print(f"* Invalid op: {s}")
            return False
    return no_dup_steps() and no_future_refs() and unused_steps()

