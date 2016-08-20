#!/usr/bin/env python

# from brat (http://brat.nlplab.org), MIT licenced.

# TODO: much of this is likely unnecessary here, clean up.

'''
Basic sentence splitter using brat segmentation to add newlines to
input text at likely sentence boundaries.
'''

import sys
from os.path import join as path_join
from os.path import dirname

from ssplit import en_sentence_boundary_gen
from common import split_keep_separator

def text_to_sentences(text, sentence_split=True):
    """Return list of sentences in given text."""

    if not sentence_split:
        sent = split_keep_separator(text)
    else:
        #sent = split_keep_separator(sentencebreaks_to_newlines(text))
        sent = split_sentences(text)

    assert ''.join(sent).replace('\n', ' ') == text.replace('\n', ' '), \
        'internal error'

    return sent

def _text_by_offsets_gen(text, offsets):
    for start, end in offsets:
        yield text[start:end]

def _normspace(s):
    import re
    return re.sub(r'\s', ' ', s)

def split_sentences(text):
    offsets = [o for o in en_sentence_boundary_gen(text)]

    # adjust to include any initial space skipped by the
    # boundary generator. (TODO: fix generator instead.)
    if offsets and offsets[0][0] > 0:
        offsets.insert(0, (0, offsets[0][0]))

    # adjust to include any intervening space
    adjusted = []
    for i in range(len(offsets)-1):
        adjusted.append((offsets[i][0], offsets[i+1][0]))
    if offsets:
        adjusted.append((offsets[-1][0], len(text)))
    offsets = adjusted

    return [s for s in _text_by_offsets_gen(text, offsets)]

def sentencebreaks_to_newlines(text):
    offsets = [o for o in en_sentence_boundary_gen(text)]

    # adjust to include any initial space skipped by the
    # boundary generator. (TODO: fix generator instead.)
    if offsets and offsets[0][0] > 0:
        offsets.insert(0, (0, offsets[0][0]))

    # break into sentences
    sentences = [s for s in _text_by_offsets_gen(text, offsets)]

    # join up, adding a newline for space where possible
    orig_parts = []
    new_parts = []

    prev_end = 0
    sentnum = len(sentences)
    for i in range(sentnum):
        sent = sentences[i]
        orig_parts.append(sent)
        new_parts.append(sent)

        if i < sentnum-1:
            orig_parts.append(text[offsets[i][1]:offsets[i+1][0]])

            if (offsets[i][1] < offsets[i+1][0] and
                text[offsets[i][1]].isspace()):
                # intervening space; can add newline
                new_parts.append('\n'+text[offsets[i][1]+1:offsets[i+1][0]])
            else:
                new_parts.append(text[offsets[i][1]:offsets[i+1][0]])

    if len(offsets) and offsets[-1][1] < len(text):
        orig_parts.append(text[offsets[-1][1]:])
        new_parts.append(text[offsets[-1][1]:])

    # sanity check
    assert text == ''.join(orig_parts), "INTERNAL ERROR:\n    '%s'\nvs\n    '%s'" % (text, ''.join(orig_parts))

    splittext = ''.join(new_parts)

    # sanity
    assert len(text) == len(splittext), "INTERNAL ERROR"
    assert _normspace(text) == _normspace(splittext), "INTERNAL ERROR:\n    '%s'\nvs\n    '%s'" % (_normspace(text), _normspace(splittext))

    return splittext

def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 2 or argv[1] == '-':
        for text in sys.stdin:
            sys.stdout.write(sentencebreaks_to_newlines(text))
    else:
        for fn in argv[1:]:
            with open(fn, 'rU') as f:
                for text in f:
                    sys.stdout.write(sentencebreaks_to_newlines(text))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
