from internallib.dependency_helpers import *

def auto_pattern1(token, all_noun_chuncks):
    dep_labels_left = []
    dep_labels_right = []

    # Pattern 1 - acl_2001_P01-1028_relate.txt
    # And (Poznanski et al., 1995) make use of a tree reconstruction method which 
    # incrementally improves the syntactic tree until it is accepted by the grammar.

    if (token.dep_ == "relcl" and token.head.pos_ == 'NOUN'):
        dep_labels_left.append(get_noun_chunck(token.head, all_noun_chuncks))
        dep_labels_right.append(pattern_based_finder_dobj_right(token, all_noun_chuncks))
    
    return {"left": dep_labels_left, "right": dep_labels_right}

def auto_pattern2(token, all_noun_chuncks):
    dep_labels_left = []
    dep_labels_right = []

    # Pattern 2 - acl_2005_P05-1071_relate.txt
    # Our work is inspired by HajicË (2000), who convincingly shows that for five Eastern
    # European languages with complex inflection plus English, using a morphological analyzer 3
    # improves performance of a tagger.

    for child in token.children:
        if (child.dep_ == "advcl" and child.pos_ == 'VERB'):
            for grandchild in child.children:
                if (grandchild.pos_ == 'NOUN'):
                    dep_labels_left.append(get_noun_chunck(grandchild, all_noun_chuncks))
                    dep_labels_right.append(pattern_based_finder_dobj_right(token, all_noun_chuncks))

                    return {"left": dep_labels_left, "right": dep_labels_right}

    return {"left": [], "right": []}

def auto_pattern3(token, all_noun_chuncks):
    dep_labels_left = []
    dep_labels_right = []

    # Pattern 3 - acl_2006_P06-1002_relate.txt
    # In recent years, researchers have shown that even using a limited amount of manually aligned data improves
    # word alignment significantly (Callison-Burch et al., 2004).

    nc = {}

    for child in token.children:
        if (child.dep_ in ["csubj", "nsubj"]):
            if (child.pos_ == 'NOUN'):
                final_token = patter_recurse_on_prep(child)
                dep_labels_left.append(get_noun_chunck(final_token, all_noun_chuncks))

            else:
                dep_labels_left.append(pattern_based_finder_dobj_right(child, all_noun_chuncks))
            
            dep_labels_right.append(pattern_based_finder_dobj_right(token, all_noun_chuncks))

            # break

    return {"left": dep_labels_left, "right": dep_labels_right}

def auto_pattern4(token, all_noun_chuncks):
    dep_labels_left = []
    dep_labels_right = []
    
    # Pattern 4 - acl_2006_P06-1078_relate.txt
    # Using many ASR hypotheses helps recover the ASR errors of NE words in 1-best ASR results and improves NER accuracy.

    another_subj = token
    if (token.dep_ == "conj"):
        another_subj = token.head

    result = auto_pattern3(another_subj, all_noun_chuncks)

    if (len(result["left"]) > 0):
        dep_labels_right.append(pattern_based_finder_dobj_right(token, all_noun_chuncks))
        result["right"] = dep_labels_right

    return result