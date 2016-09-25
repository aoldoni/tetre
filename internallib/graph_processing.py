from nltk import Tree
from types import FunctionType
from internallib.dependency_helpers import *
from internallib.rule_applier import *
import inspect
from functools import wraps

class Growth(RuleApplier):
    def __init__(self):
        RuleApplier.__init__(self)
        self.subs = ['nsubj', 'csubj', 'nsubjpass', 'csubjpass']

    @RuleApplier.register_function
    def replace_on_relcl(self, root, node_set, spacy_tree):

        upwards = ["relcl"]
        downwards = "nsubj"

        #adjust representation
        has_subj = False

        for node in node_set:
            if node in self.subs:
                has_subj = True

        if not has_subj:
            node_set.append(downwards)

        #adjust tree
        token = spacy_tree
        token_head = spacy_tree
        if (token_head.dep_ in upwards and token_head.head != token):
            token_head = token_head.head

            children_list = token.children[:]
            for i in range(0, len(children_list)):
                if (children_list[i].dep_ in self.subs):
                    token.children.pop(i)

            children_list = token_head.children[:]
            for i in range(0, len(children_list)):
                if (children_list[i].orth_ == token.orth_):
                    token_head.children.pop(i)

            token_head.dep_ = downwards
            token.children.append(token_head)

        return root, node_set, spacy_tree

    @RuleApplier.register_function
    def recurse_on_conj(self, root, node_set, spacy_tree):

        upwards = ["conj"]

        #adjust representation
        token = spacy_tree
        token_head = spacy_tree

        while True:

            if (token_head.dep_ in upwards and token_head.head != token):
                token_head = token_head.head

                for child in token_head.children:
                    if child.dep_ in self.subs:
                        node_set.append(child.dep_ )
            else:
                break


        #adjust actual tree
        token = spacy_tree
        token_head = spacy_tree

        while True:

            if (token_head.dep_ in upwards and token_head.head != token_head):
                token_head = token_head.head

                needs_loop = True
                while needs_loop:

                    changed = False
                    children_list = token_head.children[:]
                    for i in range(0, len(children_list)):

                        if token_head.children[i].dep_ in self.subs:
                            token.children.append(token_head.children[i])
                            token_head.children.pop(i)
                            changed = True
                            break

                    if not changed:
                        needs_loop = False

            else:
                break

        return root, node_set, spacy_tree

class Reduction(RuleApplier):
    def __init__(self):
        RuleApplier.__init__(self)

    @RuleApplier.register_function
    def remove_duplicates(self, root, node_set, spacy_tree):
        return root, set(node_set), spacy_tree

    @RuleApplier.register_function
    def remove_tags(self, root, node_set, spacy_tree):
        node_set = set(node_set) - self.tags_to_be_removed

        for child in spacy_tree.children:
            if child.dep_ in self.tags_to_be_removed:
                child.nofollow = True

        return root, node_set, spacy_tree

    @RuleApplier.register_function
    def tranform_tags(self, root, node_set, spacy_tree):
        node_set = set([self.rewrite_dp_tag(node) for node in node_set])
        return root, node_set, spacy_tree

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