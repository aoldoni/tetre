#!/usr/bin/env python3

### import everything
from corpkit import *
from corpkit.dictionaries import *
from nltk.corpus import wordnet as wn

query_list = []

for synset in wn.synsets('improves'):
    query_list = query_list + synset.lemma_names()
    print(synset.lemma_names())

query_list = list(set(query_list))

# q = r'/improves/'

# unparsed = Corpus('data/input-corpus/')
# corpus = unparsed.parse()

corpus = Corpus('data/input-corpus-single-parsed/')

lines = corpus.concordance({L: query_list}, show=[L,P])

lines.format(window=50, n=100000, columns=[L,M,R])