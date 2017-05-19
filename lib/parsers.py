import spacy
import os

from nltk import Tree
from directories import dirs
from parsers_cache import get_cached_tokens


def should_skip_file(fn):
    """List of file names that should skipped once looping through input files

    Args:
        fn: The filename to be checked.

    Returns:
        A boolean representing if the words should be skipped or not
     """
    jump_list = ["thumbs.db", ".DS_Store"]

    if any(fn in each_fn for each_fn in jump_list):
        return True
    else:
        return False


def get_uncached_tokens():
    """Loops through the input files and yields each token, avoids reading from cache files
    given that these cache files are word oriented (e.g.: they keep sentences only for specific
    words such as "improves" or "finds" and ignores all others).

    This iterator is appropriate for when all words need to be considered (e.g.: when attempting
    to calculate global statistics on the corpus).

    Yields:
        A pair with the Spacy token (spacy.Token) and its sentence (spacy.Span).
     """
    en_nlp = spacy.load('en')

    for fn in os.listdir(dirs['raw_input']['path']):

        if should_skip_file(fn):
            continue

        name = dirs['raw_input']['path'] + fn

        with open(name, 'r') as file_input:
            raw_text = file_input.read()

        en_doc = en_nlp(raw_text)

        for sentence in en_doc.sents:
            for token in sentence:
                yield token, sentence


def get_tokens(args):
    """Iterates through tokens for the given word being currently searched.

    Yields:
        A pair with the Spacy token (spacy.Token) and its sentence (spacy.Span).
    """
    sentences = get_cached_tokens(args)

    for token, sentence in sentences:
        if token.pos_ != "VERB":
            continue
            
        yield token, sentence


def highlight_word(sentence, word):
    """Given a sentence and a word, highlights the word in the sentence.

    Args:
        sentence: A longer string.
        word: A substring.

    Returns:
        The original sentence string, with all its word substrings wrapped in a <strong> HTML tag.
    """
    string_sentence = str(sentence)
    return string_sentence.replace(word, "<strong>" + word + "</strong>")
