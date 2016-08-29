from internallib.dependency_helpers import *

import logging, sys
logger = logging.getLogger('root')
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)30s()] %(message)s"
logging.basicConfig(format=FORMAT, stream=sys.stderr, level=logging.DEBUG)


def auto_pattern1(token, all_noun_chuncks):
    dep_labels_left = []
    dep_labels_right = []

    # Pattern 1 - acl_2001_P01-1028_relate.txt
    # And (Poznanski et al., 1995) make use of a tree reconstruction method which 
    # incrementally improves the syntactic tree until it is accepted by the grammar.

    if (token.dep_ == "relcl" and token.head.pos_ in ['NOUN', 'PROPN']):
        for i in pattern_based_finder_dobj_right(token, all_noun_chuncks):
            dep_labels_right.append(i)
            dep_labels_left.append(get_noun_chunck(token.head, all_noun_chuncks))
    
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
                if (grandchild.pos_ in ['NOUN', 'PROPN']):
                    for i in pattern_based_finder_dobj_right(token, all_noun_chuncks):
                        dep_labels_right.append(i)
                        dep_labels_left.append(get_noun_chunck(grandchild, all_noun_chuncks))
                    
                    return {"left": dep_labels_left, "right": dep_labels_right}

    return {"left": [], "right": []}


def auto_pattern3(token, all_noun_chuncks, use_token = None):
    dep_labels_left = []
    dep_labels_right = []

    # Pattern 3 - acl_2006_P06-1002_relate.txt
    # In recent years, researchers have shown that even using a limited amount of manually aligned data improves
    # word alignment significantly (Callison-Burch et al., 2004).

    nc = {}

    if (use_token == None):
        use_token = token

    logging.debug(["31", token])

    for child in token.children:

        logging.debug(["32", token, child, child.dep_])

        if (child.dep_ in ["csubj", "nsubj"]):
            for i in pattern_based_finder_dobj_right(use_token, all_noun_chuncks):
                
                logging.debug(["33", token, child, child.dep_, i])

                if (child.pos_ in ['NOUN', 'PROPN']):
                    for final_token in patter_recurse_on_prep(child):
                        dep_labels_left.append(get_noun_chunck(final_token, all_noun_chuncks))
                        dep_labels_right.append(i)

                else:
                    for final_token in pattern_based_finder_dobj_right(child, all_noun_chuncks):
                        dep_labels_left.append(final_token)
                        dep_labels_right.append(i)

    return {"left": dep_labels_left, "right": dep_labels_right}


def auto_pattern4(token, all_noun_chuncks, use_token = None):
    dep_labels_left = []
    dep_labels_right = []

    # Pattern 4 - acl_2006_P06-2118_relate.txt
    # However, they concluded that the contribution of linguistic motivated features,
    # such as features extracted from a syntactic parse, is insignificant, a finding they
    # attributed to unique properties of Chinese given that the same syntactic features
    # significantly improves the WSD accuracy.

    nc = {}

    if (use_token == None):
        use_token = token

    logging.debug(["31", token])

    for child in token.children:

        logging.debug(["32", token, child, child.dep_])

        if (child.dep_ in ["csubj", "nsubj"]):
            for i in pattern_based_finder_dobj_right(use_token, all_noun_chuncks):

                logging.debug(["321", token, child, child.dep_])

                if (child.pos_ in ['NOUN', 'PROPN']):
                    for final_token in patter_recurse_on_prep(child):
                        final_token_nc = get_noun_chunck(final_token, all_noun_chuncks)

                        logging.debug(["33", token, child, child.dep_, final_token])

                        # Pattern 6 - acl_2008_P08-1063_relate.txt
                        # They show that splitting Arg2 instances into subgroups based on
                        # VerbNet thematic roles improves the performance of the PropBank-based
                        # classifier.

                        if (final_token_nc == None):
                            for pattern_nc in pattern_extract_noun_chuncks(final_token, all_noun_chuncks, i):
                                dep_labels_left.append(pattern_nc)
                                dep_labels_right.append(i)

                        else:
                            dep_labels_left.append(get_noun_chunck(final_token, all_noun_chuncks))
                            dep_labels_right.append(i)
                else:
                    for final_token in pattern_based_finder_dobj_right(child, all_noun_chuncks):

                        logging.debug(["34", token, child, child.dep_, final_token])

                        dep_labels_left.append(final_token)
                        dep_labels_right.append(i)
        elif (child.dep_ in ["acl"]):

            logging.debug(["35", token, child, child.dep_, child.children])

            for grandchild in child.children:
                if grandchild.dep_ in ["csubj", "nsubj"]:
                    return auto_pattern4(child, all_noun_chuncks, use_token)

    return {"left": dep_labels_left, "right": dep_labels_right}


# def auto_pattern8(token, all_noun_chuncks, use_token = None):
#     dep_labels_left = []
#     dep_labels_right = []

#     nc = {}

#     if (use_token == None):
#         use_token = token

#     logging.debug(["81", token])
#     for child in token.children:
#         logging.debug(["82", token, child, child.dep_])
#         if (child.dep_ in ["csubj", "nsubj"]):
#             logging.debug(["820 - RIGHT HAND", token, child, child.dep_, use_token])
#             for i in pattern_based_finder_dobj_right(use_token, all_noun_chuncks):
#                 logging.debug(["821", token, child, child.dep_])
#                 if (child.pos_ in ['NOUN', 'PROPN']):
#                     logging.debug(["83 - LEFT HAND", token, child, child.dep_])
#                     for final_token in patter_recurse_on_prep(child):
#                         final_token_nc = get_noun_chunck(final_token, all_noun_chuncks)

#                         logging.debug(["831 - LEFT HAND", token, child, child.dep_, final_token, final_token_nc])

#                         if (final_token_nc == None):
#                             for pattern_nc in pattern_extract_noun_chuncks(final_token, all_noun_chuncks, i):
#                                 dep_labels_left.append(pattern_nc)
#                                 dep_labels_right.append(i)

#                         else:
#                             dep_labels_left.append(get_noun_chunck(final_token, all_noun_chuncks))
#                             dep_labels_right.append(i)

#                         logging.debug(["832 - LEFT HAND", token, child, child.dep_, final_token])
#                 else:
#                     logging.debug(["84 - LEFT HAND", token, child, child.dep_])
#                     for final_token in pattern_based_finder_dobj_right(child, all_noun_chuncks):
#                         logging.debug(["841 - LEFT HAND", token, child, child.dep_, final_token])

#                         dep_labels_left.append(final_token)
#                         dep_labels_right.append(i)
#             logging.debug(["85"])
#         elif (child.dep_ in ["acl"]):
#             logging.debug(["86", token, child, child.dep_, child.children])
#             for grandchild in child.children:
#                 if grandchild.dep_ in ["csubj", "nsubj"]:
#                     return auto_pattern8(child, all_noun_chuncks, use_token)

#     return {"left": dep_labels_left, "right": dep_labels_right}

# def auto_pattern9997(token, all_noun_chuncks):
#     dep_labels_left = []
#     dep_labels_right = []

#     # Pattern 4 - acl_2006_P06-2118_relate.txt
#     # However, they concluded that the contribution of linguistic motivated features,
#     # such as features extracted from a syntactic parse, is insignificant, a finding they
#     # attributed to unique properties of Chinese given that the same syntactic features
#     # significantly improves the WSD accuracy.

#     another_subj = token
#     if (token.dep_ in ["conj", "pcomp"]):
#         another_subj = token.head
#         return auto_pattern3(another_subj, all_noun_chuncks, token)

#     return {"left": dep_labels_left, "right": dep_labels_right}

# def auto_pattern9998(token, all_noun_chuncks):
#     dep_labels_left = []
#     dep_labels_right = []

#     # Pattern 4 - acl_2006_P06-2118_relate.txt
#     # However, they concluded that the contribution of linguistic motivated features,
#     # such as features extracted from a syntactic parse, is insignificant, a finding they
#     # attributed to unique properties of Chinese given that the same syntactic features
#     # significantly improves the WSD accuracy.

#     # Pattern 5 - acl_2006_P06-1078_relate.txt
#     # Using many ASR hypotheses helps recover the ASR errors of NE words in 1-best ASR results and improves NER accuracy.

#     another_subj = token
#     if (token.dep_ in ["conj", "pcomp"]):
#         another_subj = token.head
#         return auto_pattern4(another_subj, all_noun_chuncks, token)

#     return {"left": dep_labels_left, "right": dep_labels_right}

def auto_pattern9999(token, all_noun_chuncks):
    dep_labels_left = []
    dep_labels_right = []

    # Pattern 4 - acl_2006_P06-2118_relate.txt
    # However, they concluded that the contribution of linguistic motivated features,
    # such as features extracted from a syntactic parse, is insignificant, a finding they
    # attributed to unique properties of Chinese given that the same syntactic features
    # significantly improves the WSD accuracy.

    # Pattern 5 - acl_2006_P06-1078_relate.txt
    # Using many ASR hypotheses helps recover the ASR errors of NE words in 1-best ASR results and improves NER accuracy.

    # Pattern 9 - acl_2010_P10-1058_relate.txt
    # Wan and Paris (2008) segment sentences heuristically into clauses  before  extraction takes place,
    # and show that this improves summarization quality.

    another_subj = token

    while(another_subj.dep_ not in ["ROOT"]):
        if (another_subj.dep_ in ["conj", "pcomp", "ccomp", "advcl"]):
            another_subj = another_subj.head

            logging.debug("auto_pattern9999 - 0")

            result = auto_pattern3(another_subj, all_noun_chuncks, token)

            if (len(result["left"]) > 0 and result["left"][0] != None and \
             len(result["right"]) > 0 and result["right"][0] != None):
                return result

            logging.debug("auto_pattern9999 - 1")

            result = auto_pattern4(another_subj, all_noun_chuncks, token)

            if (len(result["left"]) > 0 and result["left"][0] != None and \
             len(result["right"]) > 0 and result["right"][0] != None):
                return result

            logging.debug("auto_pattern9999 - 2")

            # result = auto_pattern8(another_subj, all_noun_chuncks, token)

            # logging.debug("auto_pattern9999 - 3")

            # if (len(result["left"]) > 0 and result["left"][0] != None and \
            #  len(result["right"]) > 0 and result["right"][0] != None):
            #     return result
        else:
            break

    return {"left": dep_labels_left, "right": dep_labels_right}
