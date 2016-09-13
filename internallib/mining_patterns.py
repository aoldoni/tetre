import logging, sys
import pprint

from functools import reduce

from internallib.dependency_helpers import *

logger = logging.getLogger('root')
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)30s()] %(message)s"
logging.basicConfig(format=FORMAT, stream=sys.stderr, level=logging.INFO)

groups_positive = list()
groups_negative = list()
root_conditions = list()

root_conditions.append('''
    improves
       |
    dobj/NOUN
''')
def auto_extract_trees_pattern_00(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["dobj"] and child.pos_ in ["NOUN"]), None)

    if (first_child != None):
        result = to_nltk_tree_general(first_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 0, "type": True}


root_conditions.append('''
    improves
       |
    prep/ADP
       |
    pobj/PROPN
''')
def auto_extract_trees_pattern_01(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["prep"] and child.pos_ in ["ADP"]), None)
    second_child = None

    if (first_child != None):
        second_child = next((child for child in first_child.children if child.dep_ in ["pobj"] and child.pos_ in ["PROPN"]), None)

    if (second_child != None):
        result = to_nltk_tree_general(second_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 1, "type": True}


root_conditions.append('''
    improves
       |
    dobj/VERB
''')
def auto_extract_trees_pattern_02(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["dobj"] and child.pos_ in ["VERB"]), None)

    if (first_child != None):
        result = to_nltk_tree_general(first_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 2, "type": True}


root_conditions.append('''
    improves
       |
    dobj/PROPN
''')
def auto_extract_trees_pattern_03(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["dobj"] and child.pos_ in ["PROPN"]), None)

    if (first_child != None):
        result = to_nltk_tree_general(first_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 3, "type": True}


root_conditions.append('''
    improves
       |
    prep/ADP
       |
    pobj/PRON
''')
def auto_extract_trees_pattern_04(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["prep"] and child.pos_ in ["ADP"]), None)
    second_child = None

    if (first_child != None):
        second_child = next((child for child in first_child.children if child.dep_ in ["pobj"] and child.pos_ in ["PRON"]), None)

    if (second_child != None):
        result = to_nltk_tree_general(second_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 4, "type": True}


root_conditions.append('''
    improves
       |
    prep/ADP
       |
    pobj/NOUN
''')
def auto_extract_trees_pattern_05(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["prep"] and child.pos_ in ["ADP"]), None)
    second_child = None

    if (first_child != None):
        second_child = next((child for child in first_child.children if child.dep_ in ["pobj"] and child.pos_ in ["NOUN"]), None)

    if (second_child != None):
        result = to_nltk_tree_general(second_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 5, "type": True}


root_conditions.append('''
    improves
       |
    prep/ADP
       |
    pobj/ADJ
''')
def auto_extract_trees_pattern_06(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["prep"] and child.pos_ in ["ADP"]), None)
    second_child = None

    if (first_child != None):
        second_child = next((child for child in first_child.children if child.dep_ in ["pobj"] and child.pos_ in ["ADJ"]), None)

    if (second_child != None):
        result = to_nltk_tree_general(second_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 6, "type": True}


root_conditions.append('''
    improves
       |
    prep/PART
       |
    pobj/NOUN
''')
def auto_extract_trees_pattern_07(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["prep"] and child.pos_ in ["PART"]), None)
    second_child = None

    if (first_child != None):
        second_child = next((child for child in first_child.children if child.dep_ in ["pobj"] and child.pos_ in ["NOUN"]), None)

    if (second_child != None):
        result = to_nltk_tree_general(second_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 7, "type": True}


root_conditions.append('''
    improves
       |
    dep/NUM
''')
def auto_extract_trees_pattern_08(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["dep"] and child.pos_ in ["NUM"]), None)

    if (first_child != None):
        result = to_nltk_tree_general(first_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 8, "type": True}


root_conditions.append('''
    improves
       |
    dobj/NUM
''')
def auto_extract_trees_pattern_09(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["dobj"] and child.pos_ in ["NUM"]), None)

    if (first_child != None):
        result = to_nltk_tree_general(first_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 9, "type": True}


root_conditions.append('''
    improves
       |
    prep/PART
       |
    pobj/PROPN
''')
def auto_extract_trees_pattern_10(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["prep"] and child.pos_ in ["PART"]), None)
    second_child = None

    if (first_child != None):
        second_child = next((child for child in first_child.children if child.dep_ in ["pobj"] and child.pos_ in ["PROPN"]), None)

    if (second_child != None):
        result = to_nltk_tree_general(second_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 10, "type": True}


root_conditions.append('''
          dobj/NOUN
              |
              |
    relcl/improves/VERB
''')
def auto_extract_trees_pattern_11(token):
    result = None
    is_result = False

    if token.dep_ in ["relcl"] and token.pos_ in ["VERB"] \
        and token.head.dep_ in ["dobj"] and token.head.pos_ in ["NOUN"] and token.head != token:
        result = to_nltk_tree_general(token.head)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 11, "type": True}


root_conditions.append('''
                                      VERB
              -------------------------|-------------------------
              |                                                 |
              |                                                 |
    ccomp/improves/VERB                                     conj/VERB
                                             -------------------|-------------------
                                             |                                     |
                                         nsubj/NOUN                            dobj/NOUN
''')
def auto_extract_trees_pattern_12(token):
    result = None
    is_result = False

    parent = None

    if token.dep_ in ["ccomp"] and token.pos_ in ["VERB"] \
        and token.head.pos_ in ["VERB"] and token.head != token:
        parent = token.head

    if (parent != None):
        first_child = next((child for child in parent.children if child.dep_ in ["conj"] and child.pos_ in ["VERB"]), None)
        second_child = None

        if (first_child != None):
            second_child = next((child for child in first_child.children if child.dep_ in ["nsubj"] and child.pos_ in ["NOUN"]), None)

        if (second_child != None):
            result = to_nltk_tree_general(second_child)
            is_result = True
            yield {"is_result": is_result, "result" : result, "rule" : 12, "type": True}

        second_child = None

        if (first_child != None):
            second_child = next((child for child in first_child.children if child.dep_ in ["dobj"] and child.pos_ in ["NOUN"]), None)

        if (second_child != None):
            result = to_nltk_tree_general(second_child)
            is_result = True
            yield {"is_result": is_result, "result" : result, "rule" : 12, "type": True}


    return {"is_result": is_result, "result" : result, "rule" : 12, "type": True}


root_conditions.append('''
    improves
       |
    advcl/VERB
''')
def auto_extract_trees_pattern_13(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["advcl"] and child.pos_ in ["VERB"]), None)

    if (first_child != None):
        result = to_nltk_tree_general(first_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 13, "type": True}


root_conditions.append('''
    improves
       |
    xcomp/VERB
''')
def auto_extract_trees_pattern_14(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["xcomp"] and child.pos_ in ["VERB"]), None)

    if (first_child != None):
        result = to_nltk_tree_general(first_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 14, "type": True}


root_conditions.append('''
    improves
       |
    prep/ADP
       |
    pcomp/VERB
''')
def auto_extract_trees_pattern_15(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["prep"] and child.pos_ in ["ADP"]), None)
    second_child = None

    if (first_child != None):
        second_child = next((child for child in first_child.children if child.dep_ in ["pcomp"] and child.pos_ in ["VERB"]), None)

    if (second_child != None):
        result = to_nltk_tree_general(second_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 15, "type": True}


root_conditions.append('''
    improves
       |
    ccomp/VERB
''')
def auto_extract_trees_pattern_16(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["ccomp"] and child.pos_ in ["VERB"]), None)

    if (first_child != None):
        result = to_nltk_tree_general(first_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 16, "type": True}


root_conditions.append('''
          conj/VERB
              |
              |
    nsubj/improves/VERB
''')
def auto_extract_trees_pattern_17(token):
    result = None
    is_result = False

    if token.dep_ in ["nsubj"] and token.pos_ in ["VERB"] \
        and token.head.dep_ in ["conj"] and token.head.pos_ in ["VERB"] and token.head != token:
        result = to_nltk_tree_general(token.head)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 17, "type": True}


root_conditions.append('''
    improves
       |
    ccomp/VERB
       |
    nsubj/PROPN
''')
def auto_extract_trees_pattern_18(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["ccomp"] and child.pos_ in ["VERB"]), None)
    second_child = None

    if (first_child != None):
        second_child = next((child for child in first_child.children if child.dep_ in ["nsubj"] and child.pos_ in ["PROPN"]), None)

    if (second_child != None):
        result = to_nltk_tree_general(second_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 18, "type": True}


root_conditions.append('''
    improves
       |
    nsubj/NOUN
''')
def auto_extract_trees_pattern_19(token):
    result = None
    is_result = False

    first_child = next((child for child in token.children if child.dep_ in ["nsubj"] and child.pos_ in ["NOUN"]), None)

    if (first_child != None):
        result = to_nltk_tree_general(first_child)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 19, "type": True}





root_conditions.append('''
    conj/improves/VERB
''')
def auto_extract_trees_pattern_20(token):
    result = None
    is_result = False

    if token.dep_ in ["conj"] and token.pos_ in ["VERB"]:
        result = to_nltk_tree_general(token)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 20, "type": False}


root_conditions.append('''
    csubj/improves/VERB
''')
def auto_extract_trees_pattern_21(token):

    result = None
    is_result = False

    if token.dep_ in ["csubj"] and token.pos_ in ["VERB"]:
        result = to_nltk_tree_general(token)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 21, "type": False}


root_conditions.append('''
    advcl/improves/VERB
''')
def auto_extract_trees_pattern_22(token):

    result = None
    is_result = False

    if token.dep_ in ["advcl"] and token.pos_ in ["VERB"]:
        result = to_nltk_tree_general(token)
        is_result = True

    return {"is_result": is_result, "result" : result, "rule" : 22, "type": False}





def group_accounting_add(result, sentence, file, groups):
    found = False

    if (not result["is_result"]):
        return

    for group in groups:
        if (group["representative"] == result["result"]):
            group["sum"] = group["sum"] + 1
            group["sentences"].append({"sentence" : sentence, "file" : file, "rule" : result["rule"], "type" : result["type"]})
            found = True

    if (not found):
        groups.append({"representative" : result["result"], \
            "sum" : 1, \
            "sentences" : [ \
                {"sentence" : sentence, "file" : file, "rule" : result["rule"], "type" : result["type"]} \
            ]})

def group_accounting(result, sentence, file):
    if (result["type"]):
        group_accounting_add(result, sentence, file, groups_positive)
    else:
        group_accounting_add(result, sentence, file, groups_negative)

def group_print(groups, i, type):
    pp = pprint.PrettyPrinter(indent=4)

    threshold_sum_to_print = 0

    print("---------------------------------------------------------------")
    print("TYPE OF RESULTS:             ", type)
    print("TOTAL OF SENTENCES PARSED:   ", i)
    print("TOTAL OF EXTRACTIONS PARSED: ", reduce(lambda x, y: x + y["sum"], groups, 0))
    print("TOTAL OF PATTERNS:           ", len(groups))
    print("---------------------------------------------------------------")
    for c in range(0, len(root_conditions)):
        print(c)
        print(root_conditions[c])
    print("---------------------------------------------------------------")

    for group in groups:
        if group["sum"] <= threshold_sum_to_print:
            continue

        print()
        try:
            group["representative"].pretty_print()
        except AttributeError:
            print(group["representative"])
        
        print()
        print("# FOUND:             ", group["sum"])
        print()
        print("SAMPLES:")
        print()

        for sentences in group["sentences"]:
            print("SENTENCE:            ", str(sentences["sentence"]).replace("\r","").replace("\n","").strip())
            print("FILE:                ", sentences["file"])
            print("FOUND BY RULE:       ", sentences["rule"])
            print()

        print("---------------------------------------------------------------")

    # pp.pprint([group for group in group_sorting(groups) if group["sum"] > threshold_sum_to_print])
    # print("----------------------------------------------------")
