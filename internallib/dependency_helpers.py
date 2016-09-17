import sys
import itertools
import os

from nltk import Tree

import spacy
import spacy.en

from internallib.directories import *


import logging, sys
logger = logging.getLogger('root')
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)30s()] %(message)s"
logging.basicConfig(format=FORMAT, stream=sys.stderr, level=logging.INFO)

def pattern_extract_noun_chuncks(token, all_noun_chuncks, repeatable_token):

    nc = clean_none_from_array([get_noun_chunck(token, all_noun_chuncks)])
    result = []

    if (len(nc) == 0):
        for child in token.children:
            nc = nc + clean_none_from_array([get_noun_chunck(child, all_noun_chuncks)])

        for n in nc:
            result.append(" ".join([str(token), str(n)]))

        return result

    return nc[0]

def clean_none_from_array(list_with):
    return [x for x in list_with if x is not None]

def pattern_based_finder_dobj_right(token, all_noun_chuncks):
    nc = None

    where_to_dobj_from = token

    logging.debug(["p0", token])

    for child in where_to_dobj_from.children:

        logging.debug(["p1", token, child, child.dep_ ])

        # Pattern 10 - acl_2015_P15-2093_relate.txt
        # While matrix factorization is widely used in recommender systems,
        # matrix co-factorization helps to handle multiple aspects of the data and improves in
        # predicting individual decisions (Hong et al.

        if (child.dep_ in ["dobj", "xcomp", "compound", "prep"]):

            logging.debug(["p2"])

            for i in patter_recurse_on_prep(child):
                nc = get_noun_chunck(i, all_noun_chuncks)

                logging.debug(["p3", i, token, child, child.dep_, nc])
                
                yield nc

def patter_recurse_on_prep(token):

    where_to_dobj_from = token

    logging.debug(["c0", token, token.pos_])

    if (token.pos_ in ['NOUN', 'PROPN']):
        yield token
    
    prep_found = False
    for child in token.children:
        logging.debug(["c1", token, child, child.dep_, child.orth_ ])
        if (child.dep_ == "prep" and child.orth_ == "of"):
            prep_found = True
            where_to_dobj_from = child

    logging.debug(["c2", prep_found])

    if prep_found:
        for grangrandchild in where_to_dobj_from.children:
            logging.debug(["c3", token, where_to_dobj_from, grangrandchild, grangrandchild.pos_])
            if (grangrandchild.pos_ in ['NOUN', 'PROPN']):
                yield from patter_recurse_on_prep(grangrandchild)
    elif (token.pos_ not in ['NOUN', 'PROPN']):

        # Pattern 7 - acl_2008_P08-1082_relate.txt
        # Recent work has showed that structured retrieval improves answer ranking for factoid questions

        logging.debug(["c4"])
        child_list = list(token.children)
        if (len(child_list) == 1):
            yield from patter_recurse_on_prep(child_list[0])

def get_noun_chunck(token, all_noun_chuncks):

    find = None

    for nc in all_noun_chuncks:
        if (token in list(nc)):
            return nc

    if (find == None):

        # Pattern 8 - acl_2009_P09-1056_relate.txt
        # HMM-smoothing improves on the
        # most closely related work, the Structural Correspondence Learning technique for domain
        # adaptation (Blitzer et al.

        if token.pos_ in ['NOUN', 'PROPN']:
            if (token.head is not token):
                return str(token) + " " + str(token.head)
            else:
                return token

def to_nltk_tree_general(node, attr_list = ["dep_", "pos_"], level = 99999):

    node_representation = ''

    value_list = [getattr(node, attr) for attr in attr_list]
    node_representation = "/".join(value_list)

    if level == 0:
        return node_representation

    if node.n_lefts + node.n_rights > 0:
        return Tree(node_representation, [to_nltk_tree_general(child, attr_list, level-1) for child in node.children])
    else:
        return node_representation

def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.dep_+"/"+node.orth_+"/"+node.pos_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.dep_+"/"+node.orth_+"/"+node.pos_

def print_tree(sent):
    to_nltk_tree(sent.root).pretty_print()

def zip_tuples(results):
    tuples = []

    for i in range(0, len(results["left"])):
        tuples.append( [str(results["left"][i]) , str(results["right"][i])] )

    return tuples

def prune_duplicates(results):
    b = list()

    for sublist in results:
        if sublist not in b:
            b.append(sublist)

    return b

def group_sorting(groups):
    newlist = sorted(groups, key=lambda x: x["sum"], reverse=True)
    return newlist

def get_tokens(args):
    en_nlp = spacy.load('en')

    for fn in os.listdir(args.directory+raw_input):
        if (fn == ".DS_Store"):
            continue

        name = args.directory + raw_input + fn

        raw_text = ''

        with open(name, 'r') as input:
            raw_text = input.read()

        en_doc = en_nlp(raw_text)
        

        for sentence in en_doc.sents:
            for token in sentence:
                if (token.orth_.lower() == args.word.lower()):
                    yield token, sentence