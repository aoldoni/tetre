import sys
import itertools
import os
import pickle

from nltk import Tree

import spacy
import spacy.en

from internallib.directories import *
from internallib.tree_utils import TreeNode, spacysentence_to_fullsentence

def get_cached_sentence_image(args, output_path, sentence, file_extension):
    updated_at_date = os.path.getmtime(args.directory + raw_input)
    cache_key = args.word.lower() + str(int(updated_at_date))
    cache_file = args.directory + output_cache + cache_key

    img_name = 'sentence-'+str(sentence.file_id)+"-"+str(sentence.id)
    img_path = 'images/' + img_name + "." + file_extension

    cache_file_final = output_path + 'images/' + img_name + "." + file_extension

    if args.force_clean:
        return False
    else:
        return os.path.isfile(cache_file_final)

def get_cached_tokens(args):
    sentences = []

    updated_at_date = os.path.getmtime(args.directory + raw_input)
    cache_key = args.word.lower() + str(int(updated_at_date))
    cache_file = args.directory + output_cache + cache_key + ".spacy"

    if (os.path.isfile(cache_file) and not args.force_clean):
        with open(cache_file, 'rb') as f:
            sentences = pickle.load(f)
    else:
        en_nlp = spacy.load('en')

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

            en_doc = en_nlp(raw_text)

            sentence_id = 0

            for sentence in en_doc.sents:
                sentence_id +=1
                
                sentence_tree = spacysentence_to_fullsentence(sentence, file_id, sentence_id)

                for token in sentence_tree:
                    if (token.orth_.lower() == args.word.lower()):
                        sentences.append( (token, sentence_tree) )

        with open(cache_file, "wb") as f:
            pickle.dump(sentences, f, protocol=pickle.HIGHEST_PROTOCOL)

    return sentences