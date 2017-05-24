import os
import pickle

from parsers_backend import get_tree
from directories import dirs


def get_cached_sentence_image(argv, output_path, img_path):
    """Returns if the image is already generated or not, and avoids generating if yes.

    Args:
        argv: The command line arguments.
        output_path: The path for the output folder.
        img_path: The path to the image file to be checked.

    Returns:
        A boolean flagging if image is already generated or not.
    """

    cache_file_final = output_path + img_path

    if argv.tetre_force_clean:
        return False
    else:
        return os.path.isfile(cache_file_final)


def get_cached_tokens(argv):
    """Returns the already parsed sentences containing the word being search, if the folder was not modified.

    Args:
        argv: The command line arguments.

    Returns:
        A list of tree.FullSentence objects, the sentences parsed from the raw text.
    """

    updated_at_date = os.path.getmtime(dirs['raw_input']['path'])
    cache_key = argv.tetre_word.lower() + str(int(updated_at_date))
    cache_file = dirs['output_cache']['path'] + cache_key + ".spacy"

    if os.path.isfile(cache_file) and not argv.tetre_force_clean:
        # is cached
        with open(cache_file, 'rb') as f:
            sentences = pickle.load(f)
    else:
        # is not cached, so generates it again
        sentences = get_tree(argv)

        # saves to disk
        with open(cache_file, "wb") as f:
            pickle.dump(sentences, f, protocol=pickle.HIGHEST_PROTOCOL)

    return sentences
