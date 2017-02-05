#!/usr/bin/env python

import sys
import os
import csv
import itertools

from lib.directories import *
from lib.openie import openie_to_pretty

def argparser():
    import argparse
    ap = argparse.ArgumentParser(description='Find relations in a file in a directory',
                                 usage='%(prog)s [OPTIONS] DIRECTORY_PLEASE_NAME_FULL_INPUT_PATH')
    ap.add_argument('directory')
    ap.add_argument('-u', '--use_model', action='store_true',
                    help='uses Relation Extractor with the trained model')
    ap.add_argument('-b', '--bulk_processing', action='store_true',
                    help='tries Bulk processing')

    return ap

def run_relations_separate_output(args):

    for fn in os.listdir(args.directory+raw_input):
        if (fn == ".DS_Store"):
            continue

        name = args.directory + raw_input + fn

        if (args.use_model == False):
            print "Running Stanford's OpenIE (1 per file mode)..."
            
            output_name = args.directory+output_openie + fn + '.tsv.original'
            output_processed = args.directory+output_openie + fn + '.tsv.easy'

            print "Will write to:"
            print output_name
            print output_processed

            os.system('java -cp stanford/stanford-corenlp-full-2015-12-09/*:stanford/stanford-ner-2015-12-09/lib/* -Xmx8g edu.stanford.nlp.naturalli.OpenIE -props '+config+'dblp-pipeline-openie.properties ' + name + ' 1>' + output_name)

            with open(output_name, 'r') as input, \
                open(output_processed, 'w') as output:
                for line in input.readlines():
                    output_line_split = line.split('\t')
                    output_line = openie_to_pretty(output_line_split)
                    output.write(output_line + "\n")

        elif (args.use_model == True):
            print "Running Stanford's Relation Extractor (1 per file mode)..."
            os.system('java -cp stanford/stanford-corenlp-full-2015-12-09/*:stanford/stanford-ner-2015-12-09/lib/* -Xmx8g edu.stanford.nlp.pipeline.StanfordCoreNLP -props '+config+'dblp-pipeline.properties -file ' + name)

    return

def run_relations(args):
    names = []
    filename = 'filelist.txt'

    for fn in os.listdir(args.directory+raw_input):
        if (fn == ".DS_Store"):
            continue
        names.append(args.directory +raw_input+ fn)

    with open(filename, 'w') as output:
        data = "\n".join(names)
        output.write(data)

    if (args.use_model == False):
        print "Running Stanford's OpenIE... (Bulk mode)"
        os.system('java -cp stanford/stanford-corenlp-full-2015-12-09/*:stanford/stanford-ner-2015-12-09/lib/* -Xmx8g edu.stanford.nlp.naturalli.OpenIE -props '+config+'dblp-pipeline-openie.properties -filelist ' + filename + ' 1>'+args.directory+output_openie+'/output.tsv')

    elif (args.use_model == True):
        print "Running Stanford's Relation Extractor... (Bulk mode)"
        os.system('java -cp stanford/stanford-corenlp-full-2015-12-09/*:stanford/stanford-ner-2015-12-09/lib/* -Xmx8g edu.stanford.nlp.pipeline.StanfordCoreNLP -props '+config+'dblp-pipeline.properties -filelist ' + filename)

    os.remove(filename)

    return

def regenerate(argv):
    args = argparser().parse_args(argv[1:])

    if (not args.directory.endswith("/")):
        args.directory = args.directory + "/"

    if (args.bulk_processing):
        run_relations(args)
    else:
        run_relations_separate_output(args)

if __name__ == '__main__':
    sys.exit(regenerate(sys.argv))
