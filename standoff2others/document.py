#!/usr/bin/env python

import re

from itertools import chain
from common import pairwise, sentence_to_tokens
from sentencesplit import text_to_sentences

from tagsequence import is_tag, is_start_tag, is_continue_tag, OUT_TAG

# TODO: standoff.py interface should be narrower
from standoff import Textbound, parse_textbounds, eliminate_overlaps, \
    verify_textbounds, retag_document, parse_relations, \
    relate_document

# UI identifiers for supported formats
TEXT_FORMAT = 'text'
STANDOFF_FORMAT = 'standoff'
NERSUITE_FORMAT = 'nersuite'
CONLL_FORMAT = 'conll'
BC2GM_FORMAT = 'bc2gm'

FORMATS = [
    TEXT_FORMAT,
    STANDOFF_FORMAT,
    NERSUITE_FORMAT,
    CONLL_FORMAT,
    BC2GM_FORMAT,
]
DEFAULT_FORMAT=NERSUITE_FORMAT

# TODO: remove once https://github.com/nlplab/nersuite/issues/28 is resolved
NERSUITE_TOKEN_MAX_LENGTH = 500

class Token(object):
    """Token with position in document context, tag, and optional
    features."""

    def __init__(self, text, start, tag=OUT_TAG, fvec=None):
        self.id = ''
        self.pos = ''
        self.rel = []
        self.reltype = []
        self.relorder = []
        self.tag = tag
        self.text = text
        self.start = start
        self.end = self.start + len(self.text)

        if fvec is None:
            self.fvec = []
        else:
            self.fvec = fvec[:]

        assert self.is_valid()

    def is_valid(self):
        assert self.end == self.start + len(self.text)
        assert is_tag(self.tag)
        return True

    def tagged_type(self):
        # TODO: DRY!
        assert self.tag and self.tag != OUT_TAG
        return self.tag[2:]

    def filter_BIO_tag(self):
        if len(self.tag) > 1:
            self.tag = self.tag[2:]

    def to_nersuite(self, exclude_tag=False):
        """Return Token in NERsuite format."""

        if len(self.text) > NERSUITE_TOKEN_MAX_LENGTH:
            # NERsuite crashes on very long tokens, this exceptional
            # processing seeks to protect against that; see
            # https://github.com/nlplab/nersuite/issues/28
            import sys
            print >> sys.stderr, 'Warning: truncating very long token (%d characters) for NERsuite' % len(self.text)
            text = self.text[:NERSUITE_TOKEN_MAX_LENGTH]
        else:
            text = self.text

        fields = ([self.tag] if not exclude_tag else []) + \
            [unicode(self.start), unicode(self.end), unicode(text)]
        return '\t'.join(chain(fields, self.fvec))

    def to_conll(self):
        """Return Token in CoNLL-like format."""

        self.filter_BIO_tag()

        fields = [unicode(self.text), self.tag]
        return '\t'.join(chain(fields, self.fvec))

    def to_rothandyih(self):
        # self.filter_BIO_tag()
        return self

    @classmethod
    def from_text(cls, text, offset=0):
        """Return Token for given text."""
        return cls(text, offset)

    @classmethod
    def from_nersuite(cls, line):
        """Return Token given NERsuite format representation."""

        line = line.rstrip('\n')
        fields = line.split('\t')
        try:
            tag, start, end, text = fields[:4]
        except ValueError:
            raise FormatError('NERsuite format: too few fields ("%s")' % line)
        try:
            start, end = int(start), int(end)
        except ValueError:
            raise FormatError('NERsuite format: non-int start/end ("%s")'% line)
        if end-start != len(text):
            raise FormatError('NERsuite format: length mismatch ("%s")'% line)

        return cls(text, start, tag, fields[4:])

class Sentence(object):
    """Sentence containing zero or more Tokens."""

    def __init__(self, text, base_offset, tokens):
        self.text = text
        self.base_offset = base_offset
        self.tokens = tokens[:]
        assert self.is_valid()

    def is_valid(self):
        """Return True if the Sentence is correctly composed of Tokens,
        False otherwise."""

        for t in self.tokens:
            tstart, tend = t.start-self.base_offset, t.end-self.base_offset
            assert self.text[tstart:tend] == t.text
            assert t.is_valid()
        # TODO: check that tokens are non-overlapping and fully cover
        # the Sentence text.
        return True

    def get_tagged(self, relative_offsets=False):
        """Return list of (type, start, end) based on Token tags.

        If relative_offsets is True, start and end offsets are
        relative to sentence beginning; otherwise, they are absolute
        offsets into the document text.
        """
        
        tagged = []
        first = None
        for t, next_t in pairwise(self.tokens, include_last=True):
            if is_start_tag(t.tag):
                first = t
            if first and not (next_t and is_continue_tag(next_t.tag)):
                tagged.append((first.tagged_type(), first.start, t.end))
                first = None
        if relative_offsets:
            tagged = [(t[0], t[1]-self.base_offset, t[2]-self.base_offset)
                      for t in tagged]
        return tagged

    def to_nersuite(self, exclude_tag=False):
        """Return Sentence in NERsuite format."""

        # empty "sentences" map to nothing in the NERsuite format.
        if not self.tokens:
            return ''

        # tokens with empty or space-only text are ignored
        tokens = [t for t in self.tokens if t.text and not t.text.isspace()]

        # sentences terminated with empty lines in NERsuite format
        return '\n'.join(chain((t.to_nersuite(exclude_tag) 
                                for t in tokens), ['\n']))

    def to_conll(self, exclude_tag=False):
        """Return Sentence in CoNLL-like format."""

        # empty "sentences" map to nothing
        if not self.tokens:
            return ''

        # tokens with empty or space-only text are ignored
        tokens = [t for t in self.tokens if t.text and not t.text.isspace()]
        
        # sentences terminated with empty lines
        return '\n'.join(chain((t.to_conll() for t in tokens), ['\n']))

    def to_rothandyih(self, sentence_id, exclude_tag=False):

        output = ''

        prev_tag = 'O'
        pos_to_print = []
        text_to_print = []

        rels = {}

        i = 0
        for t in self.tokens:
            if t.tag == 'O' and prev_tag == 'O':
                output += "\t".join([str(sentence_id), t.tag, str(i), 'O', t.pos, t.text, 'O', 'O', 'O']) + "\n"
                i = i+1

                prev_tag = t.tag
            elif t.tag == 'O' and prev_tag != 'O':
                output += "\t".join([str(sentence_id), prev_tag[2:], str(i), 'O', "/".join(pos_to_print), "/".join(text_to_print), 'O', 'O', 'O']) + "\n"
                i = i+1

                output += "\t".join([str(sentence_id), t.tag, str(i), 'O', t.pos, t.text, 'O', 'O', 'O']) + "\n"
                i = i+1

                pos_to_print = []
                text_to_print = []
                prev_tag = t.tag
            else:
                if (len(t.rel) > 0):
                    for r in range(len(t.rel)):
                        if (t.rel[r] not in rels):
                            rels[t.rel[r]] = ['', -1, -1]

                        if (t.relorder[r] == 'F'):
                            rels[t.rel[r]][1] = i

                        if (t.relorder[r] == 'T'):
                            rels[t.rel[r]][2] = i

                        rels[t.rel[r]][0] = t.reltype[r]

                if (t.tag[:2] == "B-" and prev_tag != 'O'):
                    output += "\t".join([str(sentence_id), prev_tag[2:], str(i), 'O', "/".join(pos_to_print), "/".join(text_to_print), 'O', 'O', 'O']) + "\n"
                    i = i+1
                    pos_to_print = []
                    text_to_print = []
                    prev_tag = t.tag

                pos_to_print.append(t.pos)
                text_to_print.append(t.text)

                prev_tag = t.tag

        if prev_tag != 'O':
            output += "\t".join([str(sentence_id), prev_tag[2:], str(i), 'O', "/".join(pos_to_print), "/".join(text_to_print), 'O', 'O', 'O']) + "\n"
            prev_tag = 'O'

        output += '\n'

        if (len(rels) > 0):
            for k, v in rels.items():
                output += str(v[1]) + " " + str(v[2]) + " " + v[0] + '\n'
            output += '\n'
        else:
            output += '\n'

        return output


    def standoffs(self, index):
        """Return sentence annotations as list of Standoff objects."""

        textbounds = []
        for type_, start, end in self.get_tagged():
            tstart, tend = start-self.base_offset, end-self.base_offset
            textbounds.append(Textbound('T%d' % index, type_, start, end,
                                        self.text[tstart:tend]))
            index += 1
        return textbounds

    def get_tags(self):
        """Return set of all tags in Sentence."""

        tags = set()
        for t in self.tokens:
            tags.add(t.tag)
        return tags

    def __len__(self):
        """Return length of Sentence in Tokens."""
        return len(self.tokens)

    @classmethod
    def from_text(cls, text, base_offset=0):
        tokens = []
        offset = 0
        for t in sentence_to_tokens(text):
            if not t.isspace():
                tokens.append(Token.from_text(t, offset+base_offset))
            offset += len(t)        

        return cls(text, base_offset, tokens)

    @classmethod
    def from_nersuite(cls, lines, base_offset=0):
        """Return Sentence given NERsuite format lines."""
        tokens = []
        for line in lines:
            tokens.append(Token.from_nersuite(line))

        if tokens:
            base_offset = tokens[0].start

        # The NERsuite format makes no record of space, so text needs
        # to be approximated.
        texts = []
        prev_offset = base_offset
        for t in tokens:
            texts.append(' ' * (t.start-prev_offset))
            texts.append(t.text)
            prev_offset = t.end
        text = ''.join(texts)

        return cls(text, base_offset, tokens)

class Document(object):
    """Text document containing zero or more Sentences."""

    def __init__(self, text, sentences):
        self.text = text
        self.sentences = sentences[:]
        self.id = None

        assert self.is_valid()

    def is_valid(self):
        """Return True if the Document is valid (correctly composed of
        Sentences etc.), False otherwise."""

        assert ''.join(s.text for s in self.sentences) == self.text
        assert not any(not s.is_valid() for s in self.sentences)
        # TODO: check that annotations are within doc span etc.
        return True

    def standoffs(self):
        """Return document annotations as list of Standoff objects."""

        index = 1
        standoffs = []
        for s in self.sentences:
            s_standoffs = s.standoffs(index)
            standoffs.extend(s_standoffs)
            index += len(s_standoffs)
        return standoffs

    def get_tags(self):
        """Return set of all tags in Document."""

        tags = set()
        for s in self.sentences:
            tags |= s.get_tags()
        return tags

    def to_nersuite(self, exclude_tag=False):
        """Return Document in NERsuite format."""

        return ''.join((s.to_nersuite(exclude_tag) for s in self.sentences))

    def to_conll(self):
        """Return Document in CoNLL-like format."""

        return ''.join((s.to_conll() for s in self.sentences))

    def to_rothandyih(self):
        output = ''
        for i, s in enumerate(self.sentences):
            output += s.to_rothandyih(sentence_id = i)

        return output

    def to_standoff(self):
        """Return Document annotations in BioNLP ST/brat-flavored
        standoff format."""

        standoffs = self.standoffs()
        return '\n'.join(unicode(s) for s in standoffs)+'\n' if standoffs else ''

    def to_bc2gm(self):
        """Return Document annotations in BioCreative 2 Gene Mention
        format."""

        lines = []
        for s in self.sentences:
            tagged = s.get_tagged(relative_offsets=True)
            tagged = [(t[0], t[1], t[2], s.text[t[1]:t[2]]) for t in tagged]
   
            # The BC2GM format ignores space when counting offsets,
            # and is inclusive for the end offset. Create mapping
            # from standard to no-space offsets and remap.
            offset_map = {}
            o = 0
            for i, c in enumerate(s.text):
                if not c.isspace():
                    offset_map[i] = o
                    o += 1                    
            tagged = [(t[0], offset_map[t[1]], offset_map[t[2]-1], t[3]) 
                      for t in tagged]

            for t in tagged:
                lines.append('%s|%d %d|%s\n' % (self.sentence_id(s), 
                                                t[1], t[2], t[3]))

        return ''.join(lines)

    def bc2gm_text(self):
        return ''.join(['%s %s\n' % (self.sentence_id(s), s.text) 
                        for s in self.sentences])

    def sentence_id(self, s):
        return 'P%sO%d' % (self.id, s.base_offset)

    def __len__(self):
        """Return length of Document in Sentences."""
        return len(self.sentences)

    @classmethod
    def from_text(cls, text, sentence_split=True):
        """Return Document with given text and no annotations."""

        sentences = []
        offset = 0
        for s in text_to_sentences(text, sentence_split):
            sentences.append(Sentence.from_text(s, offset))
            offset += len(s)

        return cls(text, sentences)

    @classmethod
    def from_nersuite(cls, text):
        """Return Document given NERsuite format file."""

        sentences = []
        lines = []
        offset = 0
        for line in split_keep_separator(text):
            if not line:
                pass
            elif not line.isspace():
                lines.append(line)
            else:
                sentences.append(Sentence.from_nersuite(lines, offset))
                if sentences[-1].tokens:
                    offset = sentences[-1].tokens[-1].end + 1 # guess
                lines = []
        if lines:
            sentences.append(Sentence.from_nersuite(lines, offset))

        # Add spaces for gaps implied by token positions but not
        # explitly recorded in NERsuite format
        for s, next_s in pairwise(sentences):
            if s.tokens and next_s.tokens:
                gap = next_s.tokens[0].start - s.tokens[-1].end
                s.text = s.text + ' ' * gap

        # Assure document-final newline (text file)
        if sentences and not sentences[-1].text.endswith('\n'):
            sentences[-1].text = sentences[-1].text + '\n'

        text = ''.join(s.text for s in sentences)

        return cls(text, sentences)

    @classmethod
    def from_standoff(cls, text, annotations, sentence_split=True,
                      overlap_rule=None, filepos=False):
        """Return Document given text and standoff annotations."""

        # first create a document from the text without annotations
        # with all "out" tags (i.e. "O"), then re-tag the tokens based
        # on the textbounds.

        document = cls.from_text(text, sentence_split)

        textbounds = parse_textbounds(annotations)
        relations = parse_relations(annotations, textbounds)
        verify_textbounds(textbounds, text)
        textbounds = eliminate_overlaps(textbounds, overlap_rule)
        retag_document(document, textbounds)

        # load POS tags from a file in which each line contains
        # WORD\tPOSTAG

        if filepos != False:
            relate_document(document, relations)

        return document
