#!/usr/bin/env python

# Replaces Unicode characters in input text with ASCII
# approximations based on file with mappings between the two.

from __future__ import with_statement

import sys
import os
import codecs
import re

from types import StringTypes
from StringIO import StringIO
from logging import warn

# The name of the file from which to read the replacement. Each line
# should contain the hex code for the unicode character, TAB, and
# the replacement string.

MAPPING_FILE_NAME = "entities.dat"

u2a_mapping = None

# For statistics and summary of missing mappings in verbose mode
map_count = {}
missing_mapping = {}

# Support wide unichr on narrow python builds. From @marcovzla, see
# https://github.com/spyysalo/nxml2txt/pull/4.
def wide_unichr(i):
    try:
        return unichr(i)
    except ValueError:
        return (r'\U' + hex(i)[2:].zfill(8)).decode('unicode-escape')

def read_mapping(f, fn="mapping data"):
    """
    Reads in mapping from Unicode to ASCII from the given input stream
    and returns a dictionary keyed by Unicode characters with the
    corresponding ASCII characters as values. The expected mapping
    format defines a single mapping per line, each with the format
    CODE\tASC where CODE is the Unicode code point as a hex number and
    ASC is the replacement ASCII string ("\t" is the literal tab
    character). Any lines beginning with "#" are skipped as comments.
    """

    # read in the replacement data
    linere = re.compile(r'^([0-9A-Za-z]{4,})\t(.*)$')
    mapping = {}

    for i, l in enumerate(f):
        # ignore lines starting with "#" as comments
        if len(l) != 0 and l[0] == "#":
            continue

        m = linere.match(l)
        assert m, "Format error in %s line %s: '%s'" % (fn, i+1, l.replace("\n","").encode("utf-8"))
        c, r = m.groups()

        c = wide_unichr(int(c, 16))
        assert c not in mapping or mapping[c] == r, "ERROR: conflicting mappings for %.4X: '%s' and '%s'" % (ord(c), mapping[c], r)

        # exception: literal '\n' maps to newline
        if r == '\\n':
            r = '\n'

        mapping[c] = r

    return mapping

def convert_u2a(f, out=None, mapping=None):
    """
    Applies the given mapping to replace characters other than 7-bit
    ASCII from the given input stream f, writing the mapped text to
    the given output stream out.
    """
    global map_count, missing_mapping, u2a_mapping

    if mapping is None:
        mapping = u2a_mapping

    if isinstance(f, StringTypes):
        f = StringIO(f)

    is_strio = False
    if out is None:
        out = StringIO()
        is_strio = True

    for c in f.read():
        if ord(c) >= 128:
            # higher than 7-bit ASCII, might wish to map
            if c in mapping:
                map_count[c] = map_count.get(c,0)+1
                c = mapping[c]
            else:
                missing_mapping[c] = missing_mapping.get(c,0)+1
                # escape into numeric Unicode codepoint
                c = "<%.4X>" % ord(c)
        out.write(c.encode("utf-8"))

    if is_strio:
        return out.getvalue()
    else:
        return out

def print_summary(out, mapping):
    """
    Prints human-readable summary of statistics and missing mappings
    for the input into the given output stream.
    """

    global map_count, missing_mapping, u2a_mapping

    if mapping is None:
        mapping = u2a_mapping

    print >> out, "Characters replaced       \t%d" % sum(map_count.values())    
    sk = map_count.keys()
    sk.sort(lambda a,b : cmp(map_count[b],map_count[a]))
    for c in sk:
        try:
            print >> out, "\t%.4X\t%s\t'%s'\t%d" % (ord(c), c.encode("utf-8"), mapping[c], map_count[c])
        except:
            print >> out, "\t%.4X\t'%s'\t%d" % (ord(c), mapping[c], map_count[c])
    print >> out, "Characters without mapping\t%d" % sum(missing_mapping.values())
    sk = missing_mapping.keys()
    sk.sort(lambda a,b : cmp(missing_mapping[b],missing_mapping[a]))
    for c in sk:
        try:
            print >> out, "\t%.4X\t%s\t%d" % (ord(c), c.encode("utf-8"), missing_mapping[c])
        except:
            print >> out, "\t%.4X\t?\t%d" % (ord(c), missing_mapping[c])

def argparser():
    """
    Returns an argument parser for the script.
    """
    import argparse
    ap=argparse.ArgumentParser(description="Replaces Unicode characters in input text with ASCII approximations.")
    ap.add_argument('-d', '--directory', default=None, help="Directory for output (stdout by default)")
    ap.add_argument('-v', '--verbose', default=False, action='store_true', help="Verbose output")
    ap.add_argument('file', nargs='+', help='Input text file')
    return ap

def read_u2a_data():
    global u2a_mapping

    # don't read twice
    if u2a_mapping is not None:
        return u2a_mapping

    mapfn = MAPPING_FILE_NAME

    if not os.path.exists(mapfn):
        # fall back to trying in script dir
        mapfn = os.path.join(os.path.dirname(__file__), 
                             os.path.basename(MAPPING_FILE_NAME))

    with codecs.open(mapfn, encoding="utf-8") as f:
        u2a_mapping = read_mapping(f, mapfn)
    
    return u2a_mapping

def log_missing_ascii_mappings(write=warn):
    if len(missing_mapping) == 0:
        return
    write("Characters without ASCII mapping: %d" %
          sum(missing_mapping.values()))
    sk = missing_mapping.keys()
    sk.sort(lambda a,b : cmp(missing_mapping[b],missing_mapping[a]))
    for c in sk:
        try:
            write("\t%.4X\t%s\t%d" % (ord(c), c.encode("utf-8"),
                                      missing_mapping[c]))
        except:
            write("\t%.4X\t?\t%d" % (ord(c), missing_mapping[c]))

def main(argv):
    options = argparser().parse_args(argv[1:])

    # read in mapping
    try:
        mapping = read_u2a_data()
    except IOError, e:
        print >> sys.stderr, "Error reading mapping from %s: %s" % (MAPPING_FILE_NAME, e)
        return 1

    # primary processing
    for fn in options.file:
        try:
            with codecs.open(fn, encoding="utf-8") as f:
                if options.directory is None:
                    convert_u2a(f, sys.stdout, mapping)
                else:
                    bfn = os.path.basename(fn)
                    ofn = os.path.join(options.directory, bfn)
                    with codecs.open(ofn, 'wt', encoding="utf-8") as out:
                        convert_u2a(f, out, mapping)
        except IOError, e:
            print >> sys.stderr, "Error processing %s: %s" % (fn, e)

    # optionally print summary of mappings
    if options.verbose:
        print_summary(sys.stderr, mapping)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
