from nltk import Tree
from types import FunctionType
from internallib.dependency_helpers import *
from internallib.rule_applier import *
import inspect
from functools import wraps

class Extraction(RuleApplier):
    def __init__(self):
        RuleApplier.__init__(self)

    @RuleApplier.register_function
    def raw_subsentences(self, root, node_set, spacy_tree):
        result = {}

        for child in spacy_tree.children:
            # print(child, child.dep_, child.nofollow)
            if child.nofollow:
                continue

            if child.dep_ not in result:
                result[child.dep_] = []

            result[child.dep_].append(child.to_sentence_string())

        return result

    def apply(self, nltk_tree, spacy_tree):
        root = nltk_tree.label()
        node_set = [node for node in nltk_tree]

        relations = []
        
        for rule in self.get_rules():
            relations.append(rule(self, root, node_set, spacy_tree))
            # print(self.__class__.__name__, "during", [root, node_set])

        return relations

class ProcessExtraction(object):
    def __init__(self):
        self.extraction = Extraction()
        return

    def applyAll(self, nltk_tree, spacy_tree, sentence):
        relations = self.extraction.apply(nltk_tree, spacy_tree)
        return relations