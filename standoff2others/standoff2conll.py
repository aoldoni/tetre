#!/usr/bin/env python

from __future__ import print_function

import sys
import os
import codecs

from logging import error

from document import Document
from common import pairwise
from asciify import document_to_ascii
from unicode2ascii import log_missing_ascii_mappings
from tagsequence import TAGSETS, IO_TAGSET, IOBES_TAGSET, DEFAULT_TAGSET
from tagsequence import BIO_to_IO, BIO_to_IOBES
from standoff import OVERLAP_RULES, load_postags_into_document

OUTPUT_TYPES = ['CONLL', 'ROTHANDYIH']

def argparser():
    import argparse
    ap = argparse.ArgumentParser(description='Convert standoff to CoNLL format',
                                 usage='%(prog)s [OPTIONS] DIRECTORY')
    ap.add_argument('directory')
    ap.add_argument('-1', '--singletype', default=None, metavar='TYPE',
                    help='replace all annotation types with TYPE')
    ap.add_argument('-a', '--asciify', default=None, action='store_true',
                    help='map input to ASCII')
    ap.add_argument('-n', '--no-sentence-split', default=False,
                    action='store_true',
                    help='do not perform sentence splitting')
    ap.add_argument('-o', '--overlap-rule', choices=OVERLAP_RULES,
                    default=OVERLAP_RULES[0],
                    help='rule to apply to resolve overlapping annotations')
    ap.add_argument('-s', '--tagset', choices=TAGSETS, default=None,
                    help='tagset (default %s)' % DEFAULT_TAGSET)
    ap.add_argument('-p', '--postag', choices=TAGSETS, default=None,
                    help='tagset (default %s)' % DEFAULT_TAGSET)
    return ap

def is_standoff_file(fn):
    return os.path.splitext(fn)[1] == '.ann'

def txt_for_ann(filename):
    return os.path.splitext(filename)[0]+'.txt'

def read_ann(filename, options, encoding='utf-8', filepos = False):
    txtfilename = txt_for_ann(filename)
    with codecs.open(txtfilename, 'rU', encoding=encoding) as t_in:
        with codecs.open(filename, 'rU', encoding=encoding) as a_in:
            return Document.from_standoff(
                t_in.read(), a_in.read(),
                sentence_split = not options.no_sentence_split,
                overlap_rule = options.overlap_rule,
                filepos = filepos
            )

def replace_types_with(document, type_):
    from tagsequence import OUT_TAG, parse_tag, make_tag
    for sentence in document.sentences:
        for token in sentence.tokens:
            if token.tag != OUT_TAG:
                token.tag = make_tag(parse_tag(token.tag)[0], type_)

def retag_document(document, tagset):
    if tagset == IO_TAGSET:
        mapper = BIO_to_IO
    elif tagset == IOBES_TAGSET:
        mapper = BIO_to_IOBES
    else:
        raise ValueError('tagset {}'.format(tagset))
    for sentence in document.sentences:
        for t, next_t in pairwise(sentence.tokens, include_last=True):
            next_tag = next_t.tag if next_t is not None else None
            t.tag = mapper(t.tag, next_tag)

def convert_directory_conll(directory, options):
    files = [n for n in os.listdir(directory) if is_standoff_file(n)]
    files = [os.path.join(directory, fn) for fn in files]

    if not files:
        error('No standoff files in {}'.format(directory))
        return

    conll_data = ''

    for fn in sorted(files):
        document = read_ann(fn, options)
        if options.singletype:
            replace_types_with(document, options.singletype)
        if options.tagset:
            retag_document(document, options.tagset)
        if options.asciify:
            document_to_ascii(document)
        conll_data = conll_data + document.to_conll()
    
    return conll_data.encode('utf-8')

def convert_directory_rothandyih(directory, options, filepos):
    files = [n for n in os.listdir(directory) if is_standoff_file(n)]
    files = [os.path.join(directory, fn) for fn in files]

    if not files:
        error('No standoff files in {}'.format(directory))
        return

    conll_data = ''

    lines = []
    with open(filepos) as f:
        lines = f.readlines()

    previous_position = 0

    for fn in sorted(files):
        document = read_ann(fn, options, filepos = filepos)
        if options.singletype:
            replace_types_with(document, options.singletype)
        if options.tagset:
            retag_document(document, options.tagset)
        if options.asciify:
            document_to_ascii(document)

        previous_position = load_postags_into_document(document, filepos, previous_position, lines)

        conll_data = conll_data + document.to_rothandyih()
    
    return conll_data.encode('utf-8')

def conversion_entry(argv, which, filepos = False):
    # extra node just to compatibility with command line
    data = convert_and_return([''] + argv, which, filepos)
    return data

def convert_and_return(argv, which, filepos):
    args = argparser().parse_args(argv[1:])
    if not os.path.isdir(args.directory):
        error('Not a directory: {}'.format(args.directory))
        return 1

    if which == OUTPUT_TYPES[0]:
        data = convert_directory_conll(args.directory, args)
    elif which == OUTPUT_TYPES[1]:
        data = convert_directory_rothandyih(args.directory, args, filepos)

    if args.asciify:
        log_missing_ascii_mappings()
    return data

def main(argv):
    data = convert_and_return(argv, OUTPUT_TYPES[0])
    sys.stdout.write(data)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
