import os
import pickle

from parsers_backend import get_tree
from directories import dirs


def get_cached_sentence_image(argv, output_path, img_path):
    cache_file_final = output_path + img_path

    if argv.tetre_force_clean:
        return False
    else:
        return os.path.isfile(cache_file_final)


def get_cached_tokens(argv):
    updated_at_date = os.path.getmtime(dirs['raw_input']['path'])
    cache_key = argv.tetre_word.lower() + str(int(updated_at_date))
    cache_file = dirs['output_cache']['path'] + cache_key + ".spacy"

    if os.path.isfile(cache_file) and not argv.tetre_force_clean:
        with open(cache_file, 'rb') as f:
            sentences = pickle.load(f)
    else:
        sentences = get_tree(argv)

        with open(cache_file, "wb") as f:
            pickle.dump(sentences, f, protocol=pickle.HIGHEST_PROTOCOL)

    return sentences
