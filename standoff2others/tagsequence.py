#!/usr/bin/env python

# Various methods for working with tag sequences.

# Methods for fixing errors in BIO sequences are taken from fixbio.py.

import sys
import re

from collections import namedtuple

from common import pairwise

BIO_TAGSET, IO_TAGSET, IOBES_TAGSET = 'BIO', 'IO', 'IOBES'
TAGSETS = [BIO_TAGSET, IO_TAGSET, IOBES_TAGSET]
DEFAULT_TAGSET = BIO_TAGSET

TypedSpan = namedtuple('TypedSpan', ['type', 'start', 'end'])

# "OUT" tag used for tokens without annotation.
OUT_TAG = 'O'

# Tags indicating mention start
START_TAGS = ('B', 'S')

# Tags indicating mention continuation
CONTINUE_TAGS = ('I', 'E')

# Regular expression defining valid token tag forms
TAG_RE = re.compile(r'^([IOBES])((?:-\S+)?)$')

def is_tag(s):
    """Return True if given string is a valid BIO tag."""
    return TAG_RE.match(s)

def is_start_tag(tag):
    return tag and tag[0] in START_TAGS

def is_continue_tag(tag):
    return tag and tag[0] in CONTINUE_TAGS

def is_out_tag(tag):
    return tag and tag == OUT_TAG

def parse_tag(tag):
    """Parse given string as BIO tag and return (tag, type) pair.

    The expected format is "[BIO]-TYPE", where TYPE is any non-empty
    nonspace string, and the "-TYPE" part is optional.
    """

    m = re.match(r'^([IOBES])((?:-\S+)?)$', tag)
    assert m, 'ERROR: failed to parse tag "%s"' % tag
    ttag, ttype = m.groups()

    # Strip off starting "-" from tagged type, if any.
    if len(ttype) > 0 and ttype[0] == '-':
        ttype = ttype[1:]

    return ttag, ttype

def make_tag(ttag, ttype):
    """Inverse of parse_tag."""

    if ttype is None:
        return ttag
    else:
        return ttag+'-'+ttype

def tagged_spans(tags):
    """Given a sequence of tags, return corresponding list TypedSpan,
    i.e. (type, start, end) triples where start and end are token
    indices.

    The end index is that of the first token occurring after a tagged
    span, i.e. the spanned tokens are tokens[start:end].
    """

    # TODO: eliminate redundancy with Sentence.get_tagged() (DRY!)
    spans = []
    first = None
    index = 0
    for t, next_t in pairwise(tags, include_last=True):
        if is_start_tag(t):
            first = index
        if first is not None and not (next_t and is_continue_tag(next_t)):
            _, type_ = parse_tag(t)
            spans.append(TypedSpan(type_, first, index+1))
            first = None
        index += 1
    return spans

def BIO_to_IO(tag, next_tag=None):
    if tag == OUT_TAG:
        return tag
    else:
        return make_tag('I', parse_tag(tag)[1])

def BIO_to_IOBES(tag, next_tag):
    if tag == OUT_TAG:
        return tag
    elif is_start_tag(tag):
        if next_tag is not None and is_continue_tag(next_tag):
            # start of multi-token span
            return tag
        else:
            # single
            return make_tag('S', parse_tag(tag)[1])
    else:
        if next_tag is not None and is_continue_tag(next_tag):
            # continuation of multi-token span
            return tag
        else:
            # end
            return make_tag('E', parse_tag(tag)[1])

def fix_sentence_BIO(sentence):
    """Corrects BIO sequence errors in given Sentence by modifying
    Token tag attributes.
    """

    # Extract tags into format used by old fixbio functions, invoke
    # fix_BIO() to do the work, and re-insert tags. Empty "sentences"
    # are inored.

    if not sentence.tokens:
        return
    tags = [[t.tag] for t in sentence.tokens]
    fix_BIO([tags], [0])
    for i, token in enumerate(sentence.tokens):
        token.tag = tags[i][0]

    # try predicted tags also
    try:
        tags = [[t.predicted_tag] for t in sentence.tokens]
        fix_BIO([tags], [0])
        for i, token in enumerate(sentence.tokens):
            token.predicted_tag = tags[i][0]
    except AttributeError:
        # no predicted tags; fine.
        pass

class ParseError(Exception):
    def __init__(self, line, linenum, message=None, filename=None):
        self.line = line
        self.linenum = linenum
        self.message = message
        self.file = file

        if self.message is None:
            self.message = 'Parse error'

    def __str__(self):
        return (self.message +
                (' on line %d' % self.linenum) + 
                ('' if self.file is None else ' in file %s' % self.file) +
                (': "%s"' % self.line))

def BIO_indices(blocks, is_bio=is_tag):
    """Return indices of fields containing BIO tags.

    Expects output of parse_conll() (or similar) as input.

    Args:
        blocks (list of lists of lists of strings): parsed CoNLL-style input.
        is_bio: function returning True iff given a valid BIO tag.
    Returns:
        list of integers: indices of valid BIO tags in data.
    """

    valid = None
    for block in blocks:
        for line in block:
            # Initialize candidates on first non-empty
            if valid is None:
                valid = range(len(line))

            valid = [i for i in valid if i < len(line) and is_bio(line[i])]

            # Short-circuit
            if len(valid) == 0:
                return valid

    if valid is None:
        return []

    return valid

def _fix_BIO_index(blocks, index):
    """Implement fix_BIO() for single index."""

    global fix_bio_options

    # Fix errors where non-"O" sequence begins with "I" instead of "B"
    for block in blocks:
        prev_tag = None
        for line in block:
            ttag, ttype = parse_tag(line[index])
            if (prev_tag is None or prev_tag == 'O') and ttag == 'I':
                if fix_bio_options and fix_bio_options.verbose:
                    # TODO: log instead of stderr
                    print >> sys.stderr, \
                        'Rewriting initial "I" -> "B" (%s)' % ttype
                line[index] = make_tag('B', ttype)

            prev_tag = ttag

    # Fix errors where type changes without a "B" at the boundary
    for block in blocks:
        prev_tag, prev_type = None, None
        for ln, line in enumerate(block):
            ttag, ttype = parse_tag(line[index])

            if prev_tag in ('B', 'I') and  ttag == 'I' and prev_type != ttype:

                if fix_bio_options and fix_bio_options.first_type:
                    # Propagate first type to whole sequence
                    if fix_bio_options and fix_bio_options.verbose:
                        # TODO: log instead of stderr
                        print >> sys.stderr, 'Rewriting multi-type sequence ' \
                            'to first type (%s->%s)' % (ttype, prev_type)
                    i = ln
                    while i < len(block):
                        itag, itype = parse_tag(block[i][index])
                        if itag != 'I':
                            break
                        block[i][index] = make_tag(itag, prev_type)
                        i += 1
                    # Current was changed
                    ttype = prev_type

                elif (not fix_bio_options) or fix_bio_options.last_type:
                    # Propagate last type to whole sequence
                    if fix_bio_options and fix_bio_options.verbose:
                        # TODO: log instead of stderr
                        print >> sys.stderr, 'Rewriting multi-type sequence ' \
                            'to last type (%s->%s)' % (prev_type, ttype)
                    i = ln - 1
                    while i >= 0:
                        itag, itype = parse_tag(block[i][index])
                        if itag not in ('B', 'I'):
                            break
                        block[i][index] = make_tag(itag, ttype)
                        if itag == 'B':
                            break  # valid now
                        i -= 1

                elif fix_bio_options and fix_bio_options.split_multi:
                    # Split sequence
                    if fix_bio_options and fix_bio_options.verbose:
                        # TODO: log instead of stderr
                        print >> sys.stderr, 'Rewriting "I" -> "B" to split ' \
                            'at type switch (%s->%s)' % (prev_type, ttype)
                    line[index] = make_tag('B', ttype)

                else:
                    assert False, 'INTERNAL ERROR'
            
            prev_tag, prev_type = ttag, ttype

    return blocks

def fix_BIO(blocks, indices):
    """Corrects BIO tag sequence errors in given data.

    Expects output of parse_conll() (or similar) as input.
    NOTE: Modifies given blocks.

    Args:
        blocks (list of lists of lists of strings): parsed CoNLL-style input.
        indices (list of ints): indices of fields containing BIO tags.
    Returns:
        given blocks with fixed BIO tag sequence.
    """

    assert len(indices) > 0, 'Error: fix_BIO() given empty indices'

    for i in indices:
        blocks = _fix_BIO_index(blocks, i)

    return blocks

def _line_is_empty(l):
    return not l or l.isspace()

def parse_conll(input, filename=None, separator='\t', is_empty=_line_is_empty):
    """Parse CoNLL-style input.

    Input should consist of blocks of lines separated by empty lines
    (is_empty), each non-empty line consisting of fields separated by
    the given separator.

    Returns:
        list of lists of lists: blocks, lines, fields.
    """

    li, l = 0, None
    try:
        blocks = []
        current_block = []
        for l in input:
            l = l.rstrip()
            li += 1
            if is_empty(l):
                blocks.append(current_block)
                current_block = []
            else:
                current_block.append(l.split(separator))
    except Exception:
        # whatever goes wrong
        raise ParseError(l, li)

    return blocks

def process(input, indices=None):
    blocks = parse_conll(input)

    if indices is None:
        # Fix all valid unless specific indices given
        indices = BIO_indices(blocks)

    assert len(indices) > 0, 'Error: no valid BIO fields'
        
    blocks = fix_BIO(blocks, indices)

    # Output
    for block in blocks:
        for line in block:
            print '\t'.join(line)
        print

def process_file(fn, indices=None):
    with open(fn, 'rU') as f:
        return process(f, indices)

fix_bio_options = None
        
def main(argv=None):
    if argv is None:
        argv = sys.argv

    global fix_bio_options

    fix_bio_options = argparser().parse_args(argv[1:])

    # Resolve treatment of BI+ sequences with more than one type
    multi_args = [fix_bio_options.first_type, fix_bio_options.last_type, 
                  fix_bio_options.split_multi]
    assert len([a for a in multi_args if a == True]) < 2, 'At most one of the "-f", "-l" and "-s" arguments can be specified.'
    if len([a for a in multi_args if a == True]) == 0:
        # Nothing set, default
        fix_bio_options.last_type = True

    # Resolve indices to fix
    if fix_bio_options.indices is None:
        indices = None
    else:
        try:
            indices = [int(i) for i in fix_bio_options.indices.split(',')]
        except Exception:
            assert False, 'Argument "-i" value should be a comma-separated list of integers'

    # Primary processing
    for fn in fix_bio_options.files:
        try:
            if fn == '-':
                # Special case to read STDIN
                process(sys.stdin, indices)
            else:
                process_file(fn, indices)
        except Exception:            
            print >> sys.stderr, 'Error processing %s' % fn
            raise

    return 0

# from fixbio
def argparser():
    import argparse
    ap=argparse.ArgumentParser(description='Fix B-I-O sequence errors in CoNLL-style data.')
    ap.add_argument('-f', '--first-type', default=False, action='store_true', help='Use first type in for BI+ sequences with multiple types.')
    ap.add_argument('-l', '--last-type', default=False, action='store_true', help='Use first type in for BI+ sequences with multiple types (default).')
    ap.add_argument('-s', '--split-multi', default=False, action='store_true', help='Split BI+ sequences with multiple types (add Bs).')
    ap.add_argument('-i', '--indices', default=None, help='Indices of fields to fix (comma-separated)')
    ap.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose output.')
    ap.add_argument('files', nargs='+', help='Target file(s) ("-" for STDIN)')
    return ap

# from fixbio
if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except Exception, e:
        print >> sys.stderr, e
        sys.exit(1)