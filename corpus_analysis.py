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

q = r'/NN.? << improves/'

# unparsed = Corpus('data/input-corpus/')
# corpus = unparsed.parse()

corpus = Corpus('data/input-small-parsed/')

lines = corpus.concordance({T: q})
lines.format(window=50, n=100000, columns=[F,L,M,R])