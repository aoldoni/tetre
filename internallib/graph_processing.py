from nltk import Tree
from types import FunctionType
from internallib.dependency_helpers import *
import inspect
from functools import wraps

class RuleApplier(object):
    deco_list = []

    def __init__(self):
        return

    @staticmethod
    def register_function(func):
        RuleApplier.deco_list.append(func)
        return func

    def get_rules(self):
        return iter([rule for rule in RuleApplier.deco_list if self.__class__.__name__ in str(rule)])

    def apply(self, nltk_tree, spacy_tree):

        # print(self.__class__.__name__, "before", nltk_tree)

        root = nltk_tree.label()
        node_set = [node for node in nltk_tree]
        
        for rule in self.get_rules():
            root, node_set = rule(self, root, node_set, spacy_tree)
            # print(self.__class__.__name__, "during", [root, node_set])

        t = Tree(root, list(sorted(node_set)))

        # print(self.__class__.__name__, "after", t)
        # print("")

        return t

class Growth(RuleApplier):
    def __init__(self):
        RuleApplier.__init__(self)

    @RuleApplier.register_function
    def recurse_on_conj(self, root, node_set, spacy_tree):

        token = spacy_tree

        while True:
            # try:
            #     head = token.head
            # except AttributeError:
            #     root, node_set

            if (token.dep_ in ["conj"] and token.head != token):
                token = token.head

                for child in token.children:
                    if child.dep_ in ['nsubj', 'csubj', 'nsubjpass', 'csubjpass']:
                        node_set.append(child.dep_ )
                    if child.dep_ in ['dobj','iobj','pobj']:
                        node_set.append(child.dep_ )
            else:
                break

        return root, node_set

class Reduction(RuleApplier):
    def __init__(self):
        RuleApplier.__init__(self)

        self.tags_to_be_removed = set(['punct', 'cc', 'conj', 'mark'])

        ## c.f. the grouping at http://universaldependencies.org/u/dep/all.html#al-u-dep/nsubjpass
        ##
        # rule1: subject
        self.translation_rules = \
        [
            (['nsubj', 'csubj', 'nsubjpass', 'csubjpass'], 'subj'),
            (['dobj','iobj','pobj'], 'obj'),
        ]

    @RuleApplier.register_function
    def remove_duplicates(self, root, node_set, spacy_tree):
        return root, set(node_set)

    @RuleApplier.register_function
    def remove_tags(self, root, node_set, spacy_tree):
        node_set = set(node_set) - self.tags_to_be_removed
        return root, node_set

    @RuleApplier.register_function
    def tranform_tags(self, root, node_set, spacy_tree):
        node_set = set([self.rewrite_dp_tag(node) for node in node_set])
        return root, node_set

    def rewrite_dp_tag(self, tag):
        for rule in self.translation_rules:
            source_tags = rule[0]
            target_tag = rule[1]

            if tag in source_tags:
                return target_tag

        # if nothing, return itself
        return tag


class Process(object):
    def __init__(self):
        self.growth = Growth()
        self.reduction = Reduction()
        return

    def applyAll(self, nltk_tree, spacy_tree):
        nltk_tree = self.growth.apply(nltk_tree, spacy_tree)
        nltk_tree = self.reduction.apply(nltk_tree, spacy_tree)
        return nltk_tree