#!/usr/bin/env python3

import nltk
from nltk.probability import FreqDist
from nltk.util import ngrams
from nltk.corpus import stopwords

import sys
import math
import os
import xml.etree.ElementTree

from internallib.directories import *
from internallib.openie import openie_to_pretty

normalized_tags = ['CONCEPT', 'ENTITY']
ner_tag_other = 'O'

comparators = ['both_equal', 'at_least_one', 'one_gram', 'smallest_gram', 'minus_one_gram', 'at_most_two_grams']

class MockArgParser(dict):
    __getattr__= dict.__getitem__
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

def argparser():
    import argparse
    ap = argparse.ArgumentParser(description='Find relations in a file in a directory',
                                 usage='%(prog)s [OPTIONS] DIRECTORY')
    ap.add_argument('directory')

    ap.add_argument('-r', '--relation_extractor', action='store_true',
                    help='Extract relations from the Relation Extractor output')
    ap.add_argument('-i', '--open_ie', action='store_true',
                    help='Extract relations from the OpenIE output')

    ap.add_argument('-s', '--show_top', action='store_true',
                    help='show top 100 relations found by OpenIE')

    ap.add_argument('-b', '--both_equal', action='store_true',
                    help='both entities are qual in the OpenIE output')
    ap.add_argument('-a', '--at_least_one', action='store_true',
                    help='at least one entity exists in the OpenIE output')
    ap.add_argument('-p', '--at_least_percentage', nargs='?', const=0, type=int,
                    help='at least one entity exists in the OpenIE output')
    ap.add_argument('-1', '--one_gram', action='store_true',
                    help='1-gram compairson in the OpenIE output')
    ap.add_argument('-m', '--smallest_gram', action='store_true',
                    help='smallest-gram compairson in the OpenIE output')
    ap.add_argument('-o', '--minus_one_gram', action='store_true',
                    help='minus-one-gram compairson in the OpenIE output')
    ap.add_argument('-2', '--at_most_two_grams', action='store_true',
                    help='at_most_two-gram compairson in the OpenIE output')
    ap.add_argument('-t', '--output_all', action='store_true',
                    help='at_most_two-gram compairson in the OpenIE output')

    return ap

def compare_grams(multigrams1, multigrams2):
    common=[]
    for grams1 in multigrams1:
        if grams1 in multigrams2:
            common.append(grams1)
    return common

def ngram_match(line, ner, args):
    split = line.split('\t')
    e1 = split[1].upper().strip()
    e2 = split[3].upper().strip()

    e1found = False
    e2found = False

    e1split = e1.split(" ")
    e2split = e2.split(" ")

    ngram1 = len(e1split)
    ngram2 = len(e2split)

    for label in ner:
        for name in ner[label]:
            names_list = name.split(" ")
            names_gram = len(names_list)

            if (args.one_gram):
                smallest1 = 1
                smallest2 = 1

            if (args.smallest_gram):
                smallest1 = names_gram if ngram1 > names_gram else ngram1
                smallest2 = names_gram if ngram2 > names_gram else ngram2

            if (args.minus_one_gram):
                smallest1 = names_gram if ngram1 > names_gram else ngram1
                smallest2 = names_gram if ngram2 > names_gram else ngram2

                smallest1 = smallest1-1 if smallest1 > 1 else smallest1
                smallest2 = smallest2-1 if smallest2 > 1 else smallest2

            if (args.at_most_two_grams):
                smallest1 = names_gram if ngram1 > names_gram else ngram1
                smallest2 = names_gram if ngram2 > names_gram else ngram2

                smallest1 = 2 if smallest1 > 2 else smallest1
                smallest2 = 2 if smallest2 > 2 else smallest2

            gramsname1 = list(ngrams(names_list, smallest1))
            grams1 = list(ngrams(e1.split(), smallest1))

            gramsname2 = list(ngrams(names_list, smallest2))
            grams2 = list(ngrams(e2.split(), smallest2))
            
            comp1 = compare_grams(grams1, gramsname1)
            comp2 = compare_grams(grams2, gramsname2)

            if (len(comp1) > 0 and len(comp2) > 0):
                return [True, split]

            # print('-1-', gramsname1, name)
            # print('-2-', ngram1, e1, grams1, comp1)
            # print('-3-', gramsname2, name)
            # print('-4-', ngram2, e2, grams2, comp2)
            # print(split)
            # exit()

    return [False, '']

def ngram_match_percentage(line, ner, args):
    split = line.split('\t')
    e1 = split[1].upper().strip()
    e2 = split[3].upper().strip()

    e1found = False
    e2found = False

    div = 100/args.at_least_percentage

    e1split = e1.split(" ")
    e2split = e2.split(" ")

    ngram1 = math.ceil(len(e1split)/div)
    ngram2 = math.ceil(len(e2split)/div)

    if (ngram1 < 1):
        ngram1 = 1
    if (ngram2 < 1):
        ngram2 = 1

    ngram1 = 2
    ngram2 = 2

    grams1 = list(ngrams(e1.split(), ngram1))
    grams2 = list(ngrams(e2.split(), ngram2))

    for label in ner:
        for name in ner[label]:
            gramsname = list(ngrams(name.split(" "), math.ceil(len(name.split(" "))/div)))

            comp1 = compare_grams(grams1, gramsname)
            comp2 = compare_grams(grams2, gramsname)

            if (len(comp1) > 0 and len(comp2) > 0):
                return [True, split]
            # print(div, math.ceil(len(name.split(" "))/div), name, gramsname)
            # print(div, ngram1, e1, grams1, comp1)
            # print(div, ngram2, e2, grams2, comp2)
            # print(split)
            # print()

    return [False, '']

def exact_match(line, ner, args):
    split = line.split('\t')
    e1 = split[1].upper().strip()
    e2 = split[3].upper().strip()

    e1found = False
    e2found = False

    for label in ner:
        if e1 in ner[label]:
            e1found = True
        if e2 in ner[label]:
            e1found = True

    if args.both_equal:
        if e1found and e2found:
            return [True, split]
    elif args.at_least_one:
        if e1found or e2found:
            return [True, split]

    return [False, '']

def match(document, ner, args):
    relations = []

    with open(document, 'r') as input:
        for line in input.readlines():

            if (args.both_equal or args.at_least_one):
                result = exact_match(line, ner, args)

            elif (args.one_gram or args.smallest_gram or args.minus_one_gram or args.at_most_two_grams):
                result = ngram_match(line, ner, args)

            elif (args.at_least_percentage > 0):
                result = ngram_match_percentage(line, ner, args)

            if (result[0]):
                relations.append(result[1])

    return relations


def bulk_ner_openie(document):
    ner = dict((el,set([])) for el in normalized_tags)

    e = xml.etree.ElementTree.parse(document).getroot()
    sentences = list(list(e)[0])[0]

    for sentence in sentences:
        preventity = ner_tag_other
        current_ner = []
        for token in list(sentence)[0]:

            text = list(token)[0].text.upper()
            entity = list(token)[5].text.upper()

            if preventity in normalized_tags and entity != preventity:
                ner[preventity].add( " ".join(current_ner) )
                current_ner = []

            if entity in normalized_tags:
                current_ner.append(text)
            
            preventity = entity

    return ner


def print_top5_relations(args):
    relations = []

    with open('temp/output.tsv', 'r') as input:
        for line in input.readlines():
            relations.append(line.split('\t')[2])

    text = nltk.Text(relations)
    fdist = FreqDist(text)

    most_common = fdist.most_common(200)
    non_stop = []
    stopwords_set = set(stopwords.words('english'))

    for word in most_common:
        if len(set(word[0].split(" ")).intersection(stopwords_set)) == 0:
            non_stop.append(word)

    for data in stopwords.words('english'):
        print(data)
    print()

    for data in most_common:
        print(data)
    print()

    for data in non_stop:
        print(data)
    print()

    return

def parse_openie(args):

    # filename
    # if (args.both_equal or args.at_least_one):
    # result = exact_match(line, ner, args)

    # elif (args.one_gram or args.smallest_gram or args.minus_one or args.at_most_two):
    # result = ngram_match(line, ner, args)

    # elif (args.at_least_percentage > 0):
    # result = ngram_match_percentage(line, ner, args)

    for fn in os.listdir(args.directory+raw_input):
        if (fn == ".DS_Store"):
            continue

        doc = fn[:-4]
        print("Processing file {0}:".format(doc))

        directory = args.directory
        ner = bulk_ner_openie(directory+output_rel+doc+'.txt.xml')

        # print("Possible entities are:")
        # print(ner)
        # print("")

        for i in comparators:
            temp = {}

            for j in comparators:
                temp[j] = False

            temp[i] = True
            argsmock = MockArgParser(temp)

            relations = match(directory+output_openie+doc+'.txt.tsv.original', ner, argsmock)

            output_ngram_file_name = directory+output_ngram+doc+'-'+i+'.tsv'

            print("Writing to {0}:".format(output_ngram_file_name))
            
            with open(output_ngram_file_name, 'w') as output:
                for r in relations:
                    output.write("\t" + openie_to_pretty(r) + "\n")

        # print("-------------------------")
        # print("")

def parse_relation_extractor(args):
    return

def regenerate(argv):
    args = argparser().parse_args(argv[1:])

    if (not args.directory.endswith("/")):
        args.directory = args.directory + "/"

    if (args.open_ie):
        if (args.show_top):
            return print_top5_relations(args)
        else:
            return parse_openie(args)
    elif (args.relation_extractor):
        return parse_relation_extractor(args)

if __name__ == '__main__':
    sys.exit(regenerate(sys.argv))