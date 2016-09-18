#!/usr/bin/env python3

import sys
import os
import csv
import pprint
import itertools
import functools
import subprocess
import types
import logging

from functools import reduce

### import everything
from corpkit import *
from corpkit.dictionaries import *

from nltk.corpus import wordnet as wn

import spacy
import spacy.en
from nltk import Tree
from inspect import getmembers, isfunction, isgeneratorfunction

from internallib.openie import *

from internallib.directories import *
from internallib.dependency_helpers import *
from internallib.mining_patterns import *
from internallib.graph import *
from internallib import dependency_patterns
from internallib import mining_patterns
from internallib import graph

logger = logging.getLogger('root')
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)30s()] %(message)s"
logging.basicConfig(format=FORMAT, stream=sys.stderr, level=logging.INFO)

word_being_analysed = "improves"

auto_pattern_prefix = "auto_"
dependency_patterns_list = [o for o in getmembers(dependency_patterns) if isfunction(o[1])]
mining_patterns_list = [o for o in getmembers(mining_patterns) if isfunction(o[1])]

def argparser():
    import argparse
    ap = argparse.ArgumentParser(description='Analyse corpus scripts',
                                 usage='%(prog)s [OPTIONS] WORD DIRECTORY_DATA')
    ap.add_argument('directory')
    ap.add_argument('word')
    ap.add_argument('-l', '--lemma_search', action='store_true',
                    help='search for a given lemma and its variations in a parsed corpus')
    ap.add_argument('-s', '--spacy', action='store_true',
                    help='tries spacy command')
    ap.add_argument('-m', '--mine', action='store_true',
                    help='uses spacy to try to mine candidate trees')
    ap.add_argument('-g', '--graph', action='store_true',
                    help='uses spacy to generate tree graphs')
    ap.add_argument('-format', help='format of the tree node accumulator')
    ap.add_argument('-behaviour', help='groupby|listing|simplified_groupby')
    ap.add_argument('-f', '--force_clean', action='store_true',
                    help='ignores any caching and forces reprocessing')
    return ap

def lemma_search(args):
    query_list = []

    for synset in wn.synsets(word_being_analysed):
        query_list.append(synset)
        # print(synset.lemma_names())

    query_list = list(set(query_list))

    print(query_list)

    # q = r'/improves/'

    # unparsed = Corpus('data/input-corpus/')
    # corpus = unparsed.parse()

    # corpus = Corpus(args.directory)
    # lines = corpus.concordance({L: query_list}, show=[L,P])
    # lines.format(window=50, n=100000, columns=[L,M,R])

def spacy_parse(args):
    en_nlp = spacy.load('en')

    i = 0

    lines_extracted = 0
    total_relations = 0
    total_lines = 0

    process = start_openie_process()

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

                    if (i < 0):
                        continue;

                    # left = spacy_tree_noun_detection(token, token, all_noun_chuncks, 1)
                    # middel = token
                    # right = spacy_tree_noun_detection(token, token, all_noun_chuncks, -1)

                    logging.debug(fn)

                    results = spacy_pattern_based_finder(token, all_noun_chuncks)

                    process = start_openie_process()
                    results_openie = send_openie_sentence(process, str(sentence).encode('utf-8')).decode('utf-8').strip().split('\n')

                    logging.debug(all_noun_chuncks)

                    print("FILE: ", fn)
                    print("ID SEQUENCE: ", i)

                    print()
                    print_tree(sentence)
                    print()

                    print("SENTENCE: ", sentence)

                    print()

                    if (len(results) > 0):
                        print(len(results), "RELATIONS FOUND BY MANUAL PARSER!!!")
                        for result in results:
                            print("\t", token, "(" , result , ")")

                    else:
                        print("NO RELATIONS FOUND BY MANUAL PARSER.")

                    print()

                    if (len(results_openie) > 0):
                        print(len(results_openie), "RELATIONS FOUND BY OPENIE!!!")
                        for result in results_openie:
                            print("\t", openie_to_pretty(result.split("\t")))

                    else:
                        print("NO RELATIONS FOUND BY OPENIE.")

                    print()

                    if (len(results) > 0):
                        lines_extracted = lines_extracted+1

                    total_relations = total_relations + len(results)
                    total_lines = total_lines+1
                    
                    print("CURRENT STATS:")
                    print("total_sentences_found: ", lines_extracted)
                    print("total_sentences:       ", total_lines)
                    print("total_relations:       ", total_relations)
                    print("percentage:            ", "{0:.0f}%".format((100. * lines_extracted)/total_lines))

                    print()
                    print("-----------------------")
                    print()

                    i = i+1

                    if (i >= 99999999):
                        sys.exit()

def start_openie_process():
    process=subprocess.Popen('java -cp stanford/stanford-corenlp-full-2015-12-09/*:stanford/stanford-ner-2015-12-09/lib/* -Xmx8g edu.stanford.nlp.naturalli.OpenIE -props config/dblp-pipeline-openie.properties',
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True)
    return process

def send_openie_sentence(process, inputdata):
    stdoutdata,stderrdata = process.communicate(input=inputdata)
    return stdoutdata

def spacy_pattern_based_finder(token, all_noun_chuncks):

    dep_labels_left = []
    dep_labels_right = []

    result = {}
    final_reslult = {"left": [], "right": []}

    for function in dependency_patterns_list:
        if (auto_pattern_prefix in function[0]):
            result = function[1](token, all_noun_chuncks)

            logging.debug([function[0], function[1], result])

            if (len(result["left"]) > 0 and result["left"][0] != None and \
             len(result["right"]) > 0 and result["right"][0] != None):
                final_reslult["left"] = final_reslult["left"] + result["left"]
                final_reslult["right"] = final_reslult["right"] + result["right"]

    return prune_duplicates(zip_tuples(final_reslult))

def mine_pattern_based_finder(token):

    dep_labels_left = []
    dep_labels_right = []

    for function in mining_patterns_list:
        if (auto_pattern_prefix in function[0]):

            prev_result = function[1](token)

            if (isinstance(prev_result, types.GeneratorType)):
                results = list(prev_result)
            else:
                results = [prev_result]

            results = [result for result in results if result["is_result"]]

            if (len(results) > 0):
                return results

    return [{"is_result": False, "result" : None, "rule" : -1}]

def mine_candidate_trees_inner(args):
    en_nlp = spacy.load('en')

    i = 0

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
                if (token.orth_.lower() == word_being_analysed.lower()):

                    results = mine_pattern_based_finder(token)

                    for result in results:
                        group_accounting(result, sentence, fn)

                    i += 1

                    for result in results:
                        if (not result["is_result"]):
                            raise Exception("Untreated pattern!")
                            return i

    return i

def mine_candidate_trees(args):
    i = mine_candidate_trees_inner(args)
    group_print(group_sorting(groups_positive), i, True)
    group_print(group_sorting(groups_negative), i, False)

def regenerate(argv):
    args = argparser().parse_args(argv[1:])

    if (not args.directory.endswith("/")):
        args.directory = args.directory + "/"

    if args.word != False:
        word_being_analysed = args.word

    if (args.lemma_search):
        lemma_search(args)
    elif (args.spacy):
        spacy_parse(args)
    elif (args.mine):
        mine_candidate_trees(args)
    elif (args.graph):
        if (args.behaviour == "accumulator"):
            cmd = CommandAccumulative(args)
        elif (args.behaviour == "groupby"):
            cmd = CommandGroup(args)
        elif (args.behaviour == "simplified_groupby"):
            cmd = CommandSimplifiedGroup(args)
        cmd.run()

if __name__ == '__main__':
    sys.exit(regenerate(sys.argv))
