# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import re
import sys

import spacy
import spacy.en
from directories import dirs, should_skip_file
from tree_utils import spacysentence_to_fullsentence


def raw_parsing(text):
    """Applies some parsing rules to the raw text.

    Args:
        text: A string cotaining the original text of the file.

    Returns:
        The string with the file contents after being processed.
    """

    # Clear unicode
    if sys.version_info >= (3, 0):
        text = bytes.decode(str.encode(text).decode('unicode_escape').encode('ascii', 'ignore'))
    else:
        text = text.decode('unicode_escape').encode('ascii', 'ignore')

    # Remove confusin "et at." from text
    text = re.sub(r"et al\.?", "", text, flags=re.IGNORECASE)

    # Remove confusin "[1]" citation style from text
    text = re.sub(r"\([^)^(]*?\d{4}[^)^(]*?\)", "", text)

    return text


def get_tree_from_spacy(argv):
    """Parses the raw text using SpaCy.

    Args:
        argv: The command line arguments.

    Returns:
        A list of tree.FullSentence objects, the sentences parsed from the raw text.
    """

    en_nlp = spacy.en.English()

    sentences = []

    file_id = 0

    lst = os.listdir(dirs['raw_input']['path'])
    lst.sort()

    for fn in lst:
        file_id += 1

        if should_skip_file(fn):
            continue

        name = dirs['raw_input']['path'] + fn

        with open(name, 'r') as file_input:
            raw_text = file_input.read()

        if argv.tetre_word not in raw_text:
            continue

        raw_text = raw_parsing(raw_text)
        en_doc = en_nlp(raw_text)

        sentence_id = 0
        for sentence in en_doc.sents:
            sentence_id += 1

            sentence_tree = spacysentence_to_fullsentence(sentence, file_id, sentence_id)

            for token in sentence_tree:
                if token.orth_.lower() == argv.tetre_word.lower():
                    sentences.append((token, sentence_tree))

    return sentences


# def get_tree_from_stanford(argv):
#     sentences = []
#
#     file_id = 0
#
#     lst = os.listdir(dirs['raw_input']['path'])
#     lst.sort()
#
#     for fn in lst:
#         file_id += 1
#
#         if should_skip_file(fn):
#             continue
#
#         name = dirs['raw_input']['path'] + fn
#
#         raw_text = ''
#         with open(name, 'r') as file_input:
#             raw_text = file_input.read()
#
#     from nltk.parse.stanford import StanfordDependencyParser
#     dep_parser=StanfordNeuralDependencyParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
#     print [parse.tree() for parse in dep_parser.raw_parse("The quick brown fox jumps over the lazy dog.")]
#
#     return sentences


def get_tree(argv):
    """Parses the raw text using the selected backend.

    Args:
        argv: The command line arguments.

    Returns:
        A list of tree.FullSentence objects, the sentences parsed from the raw text. It is expected that
        future backends would also be transformed into such SpaCy-like structure.
    """

    if argv.tetre_backend == "spacy":
        return get_tree_from_spacy(argv)
    elif argv.tetre_backend == "stanford":
        print("Not implemented!")
        # return get_tree_from_stanford(argv)
    return
