# here goes future multiple backends implementations

from nltk.parse.stanford import StanfordDependencyParser
import os
import re

import spacy
import spacy.en

from internallib.directories import *
from internallib.tree_utils import TreeNode, spacysentence_to_fullsentence

def raw_parsing(text):
    text = text.replace("et al.", "et al")
    # text = text.replace("et al.", "")
    # text = re.sub(r"[Ã¢Â€ÂœÃ¢Â€Â•Ã¢ÂˆÂˆÃŽÂ²ÃŽÂ²ÃÂ†Ã¢Â€Â™]","")
    return text


def get_tree_from_spacy(args):
    en_nlp = spacy.en.English()
    # en_nlp = spacy.load('en')

    sentences = []

    file_id = 0

    for fn in os.listdir(args.directory+raw_input):
        file_id += 1

        if (fn == ".DS_Store"):
            continue

        name = args.directory + raw_input + fn

        raw_text = ''

        with open(name, 'r') as input:
            raw_text = input.read()

        if (args.word not in raw_text):
            continue

        raw_text = raw_parsing(raw_text)

        en_doc = en_nlp(raw_text)

        sentence_id = 0

        for sentence in en_doc.sents:
            sentence_id += 1

            sentence_tree = spacysentence_to_fullsentence(sentence, file_id, sentence_id)

            for token in sentence_tree:
                if (token.orth_.lower() == args.word.lower()):
                    sentences.append( (token, sentence_tree) )

    return sentences

def get_tree_from_stanford(args):
    sentences = []

    file_id = 0

    for fn in os.listdir(args.directory+raw_input):
        file_id += 1

        if (fn == ".DS_Store"):
            continue

        name = args.directory + raw_input + fn

        raw_text = ''

        with open(name, 'r') as input:
            raw_text = input.read()

    # dep_parser=StanfordNeuralDependencyParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
    # print [parse.tree() for parse in dep_parser.raw_parse("The quick brown fox jumps over the lazy dog.")]

    return sentences

def get_tree(args):
    if (args.backend == "spacy"):
        return get_tree_from_spacy(args)
    elif (args.backend == "stanford"):
        return get_tree_from_stanford(args)
    return
