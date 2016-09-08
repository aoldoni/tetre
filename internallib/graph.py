from graphviz import Digraph

import spacy
import spacy.en

import itertools
import operator

from internallib.dependency_helpers import *

class Command(object):
    def __init__(self, args):
        self.args = args
        self.accumulated_children = {}
        self.accumulated_parents = {}
        self.max = 50
        self.current = 0
        self.total = 0

    def run(self):
        for token in get_tokens(self.args):
            self.graph_gen_accumulate(token)

    def graph_gen_accumulate(self, token):

        if (token.dep_ not in self.accumulated_parents):
            self.accumulated_parents[token.dep_] = {}

        if (str(token.head) not in self.accumulated_parents[token.dep_]):
            self.accumulated_parents[token.dep_][str(token.head)] = 1
        else:
            self.accumulated_parents[token.dep_][str(token.head)] += 1

        for child in token.children:
            if child.dep_ not in self.accumulated_children:
                self.accumulated_children[child.dep_] = {}

            if str(child) not in self.accumulated_children[child.dep_]:
                self.accumulated_children[child.dep_][str(child)] = 1
            else:
                self.accumulated_children[child.dep_][str(child)] += 1

            self.current += 1

        if self.current > self.max:
            self.graph_gen_generate()
            sys.exit()

        return

    def graph_gen_generate(self):
        e = Digraph(self.args.word, format='png')
        e.attr('node', shape='box')

        main_node = "A"

        e.node(main_node, self.args.word)

        i = 0
        for key, value in self.accumulated_children.items():
            sorted_values = sorted(value.items(), key=operator.itemgetter(1))
            e.node(str(i), "\n".join([value[0] for value in sorted_values]))
            e.edge(main_node, str(i), label=key)
            i += 1

        for key, value in self.accumulated_parents.items():
            sorted_values = sorted(value.items(), key=operator.itemgetter(1))
            e.node(str(i), "\n".join([value[0] for value in sorted_values]))
            e.edge(str(i), main_node, label=key)
            i += 1

        e.render('output/round-table-'+str(self.total)+'.png', view=True)

        self.total += 1

        return

    def graph_gen_html(self):
        return
