#!/usr/bin/env python

import sys
import os
import csv
import itertools

from standoff2others.postag import merge_pos
from standoff2others.standoff2conll import conversion_entry, OUTPUT_TYPES
from standoff2others.standoff import load_postags_into_document
from internallib.directories import *

def clean_intermeadiate_data():
    os.system('rm '+transformed+'dblp*')

def clean_data():
    os.system('rm '+transformed+'*')
    os.system('rm '+models+'*.ser')
    os.system('rm '+models+'*.ser.gz')

def transform_ner_from_standoff(file):
    # os.system('python standoff2others/standoff2conll.py annotated/ > training/dblp.tsv')
    with open(file, 'w') as output:
        data = conversion_entry([annotated], OUTPUT_TYPES[0])
        output.write(data)

def transform_rel_from_standoff(file, filepos):
    # os.system('python standoff2others/standoff2conll.py annotated/ > training/dblp.tsv')
    with open(file, 'w') as output:
        data = conversion_entry([annotated], OUTPUT_TYPES[1], filepos)
        output.write(data)

def run_google():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    os.chdir(script_dir + "/" + google_parsey_path)
    os.system("cat ../../../"+transformed+"dblp.tsv | awk '{ print $1 }' | syntaxnet/google.sh 1>../../../"+transformed+"dblp-pos.tsv")
    os.system("awk 'NF' ../../../"+transformed+"dblp.tsv > ../../../"+transformed+"dblp-noempty.tsv")
    os.system("awk 'NF' ../../../"+transformed+"dblp-pos.tsv > ../../../"+transformed+"dblp-pos-noempty.tsv")
    os.chdir(script_dir)

def train_stanford_NER():
    os.system('java -cp "stanford/stanford-ner-2015-12-09/stanford-ner.jar:stanford/stanford-ner-2015-12-09/lib/*" edu.stanford.nlp.ie.crf.CRFClassifier -prop '+config+'dblp-ner.properties')

def train_stanford_REL():
    os.system('java -cp stanford/stanford-corenlp-full-2015-12-09/*:stanford/stanford-ner-2015-12-09/lib/* edu.stanford.nlp.ie.machinereading.MachineReading --arguments '+config+'dblp-relation.properties')

def regenerate(argv):

    print "Cleaning existing data..."
    clean_data()

    print "Generating TSV file from annotated data..."
    transform_ner_from_standoff(transformed+'dblp.tsv')

    print "Generating Part Of Speech tag using Google's Tensorflow and Syntaxnet..."
    run_google()

    print "Generating Stanford's NER inputfile..."
    merge_pos(transformed+'dblp-noempty.tsv', transformed+'dblp-pos-noempty.tsv', transformed+'stanford-ner-input.tsv')

    print "Generating CORPUS Roth and Yih's Stanford REL inputfile..."
    transform_rel_from_standoff(transformed+'stanford-rel-input.corp', transformed+'dblp-pos-noempty.tsv')

    print "Generating Model using CRFClassifier Stanford's NER..."
    train_stanford_NER()

    print "Generating Model using MachineReading Stanford's REL..."
    train_stanford_REL()

    # print "Generating Model using CRFClassifier Stanford's NER..."
    # clean_intermeadiate_data()

if __name__ == '__main__':
    sys.exit(regenerate(sys.argv))
