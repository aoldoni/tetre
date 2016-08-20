import re

from itertools import chain, tee, izip

class FormatError(Exception):
    pass

# adapted from http://docs.python.org/library/itertools.html#recipes
def pairwise(iterable, include_last=False):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    if not include_last:
        return izip(a, b)
    else:
        return izip(a, chain(b, (None, )))

# from http://programmaticallyspeaking.com/split-on-separator-but-keep-the-separator-in-python.html
def split_keep_separator(s, sep='\n'):
    return reduce(lambda acc, elem: acc[:-1] + [acc[-1] + elem] if elem == sep 
                  else acc + [elem], re.split("(%s)" % re.escape(sep), s), [])

# NERsuite tokenization: alnum sequences preserved as single tokens,
# rest are single-character tokens.
# single-character token. 
# TODO: Unicode support
TOKENIZATION_REGEX = re.compile(r'([0-9a-zA-Z]+|[^0-9a-zA-Z])')

def sentence_to_tokens(text):
    """Return list of tokens in given sentence using NERsuite tokenization."""

    tok = [t for t in TOKENIZATION_REGEX.split(text) if t]
    assert ''.join(tok) == text
    return tok
