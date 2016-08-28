#!/usr/bin/env python3

import sys
import os
import csv
import itertools

### import everything
from corpkit import *
from corpkit.dictionaries import *
from nltk.corpus import wordnet as wn

import spacy
import spacy.en
from nltk import Tree
from inspect import getmembers, isfunction

from internallib.directories import *
from internallib.dependency_helpers import *
from internallib import dependency_patterns

auto_pattern_prefix = "auto_"
word_being_analysed = "improves"
functions_list = [o for o in getmembers(dependency_patterns) if isfunction(o[1])]

def argparser():
    import argparse
    ap = argparse.ArgumentParser(description='Analyse corpus scripts',
                                 usage='%(prog)s [OPTIONS] DIRECTORY_PLEASE_NAME_FULL_INPUT_PATH')
    ap.add_argument('directory')
    ap.add_argument('-l', '--lemma_search', action='store_true',
                    help='search for a given lemma and its variations in a parsed corpus')
    ap.add_argument('-s', '--spacy', action='store_true',
                    help='tries spacy command')

    return ap

def lemma_search(args):
    query_list = []

    for synset in wn.synsets(word_being_analysed):
        query_list = query_list + synset.lemma_names()
        print(synset.lemma_names())

    query_list = list(set(query_list))

    # q = r'/improves/'

    # unparsed = Corpus('data/input-corpus/')
    # corpus = unparsed.parse()

    corpus = Corpus(args.directory)
    lines = corpus.concordance({L: query_list}, show=[L,P])
    lines.format(window=50, n=100000, columns=[L,M,R])

def spacy_parse(args):
    en_nlp = spacy.load('en')

    i = 1

    for fn in os.listdir(args.directory+raw_input):
        if (fn == ".DS_Store"):
            continue

        name = args.directory + raw_input + fn

        # name = args.directory+raw_input+'acl_2006_P06-1078_relate.txt'
        raw_text = ''

        with open(name, 'r') as input:
            raw_text = input.read()

        en_doc = en_nlp(raw_text)
        all_noun_chuncks = []

        for noun_phrase in en_doc.noun_chunks:
            all_noun_chuncks.append(noun_phrase)

        for sentence in en_doc.sents:
            for token in sentence:
                if (token.orth_.lower() == word_being_analysed.lower()):
                    # left = spacy_tree_noun_detection(token, token, all_noun_chuncks, 1)
                    # middel = token
                    # right = spacy_tree_noun_detection(token, token, all_noun_chuncks, -1)

                    # print(fn)

                    # print_tree(sentence)

                    results = spacy_pattern_based_finder(token, all_noun_chuncks)

                    print(sentence)
                    # print(all_noun_chuncks)
                    print(token, results['left'], results['right'])

                    # if (len(results["left"]) > 0 and len(results["right"]) > 0):
                        # print(results["left"], token, results["right"])
                    
                    print("------------------------")

                    i = i+1
                    if (i > 20):
                        sys.exit()

def spacy_pattern_based_finder(token, all_noun_chuncks):

    dep_labels_left = []
    dep_labels_right = []

    result = {}

    for function in functions_list:
        if (auto_pattern_prefix in function[0]):
            result = function[1](token, all_noun_chuncks)

            print(function[0], function[1], result)

            if (len(result["left"]) > 0 and result["left"][0] != None and \
             len(result["right"]) > 0 and result["right"][0] != None):
                return result

    return {"left": [], "right": []}

def regenerate(argv):
    args = argparser().parse_args(argv[1:])

    if (not args.directory.endswith("/")):
        args.directory = args.directory + "/"

    if (args.lemma_search):
        lemma_search(args)
    elif (args.spacy):
        spacy_parse(args)

if __name__ == '__main__':
    sys.exit(regenerate(sys.argv))
