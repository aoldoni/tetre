from nltk import Tree
from types import FunctionType
from internallib.dependency_helpers import *
from internallib.rule_applier import *
import inspect
from functools import wraps

class Growth(RuleApplier):
    def __init__(self):
        RuleApplier.__init__(self)

    @RuleApplier.register_function
    def recurse_on_relcl(self, root, node_set, spacy_tree):
        return root, node_set, spacy_tree

    @RuleApplier.register_function
    def recurse_on_conj(self, root, node_set, spacy_tree):

        # print("----------------------------------")
        # print("GROWTH")
        # print(root, node_set, ", ".join([str(child) for child in spacy_tree.children]))

        upwards = ["conj"]
        subs = ['nsubj', 'csubj', 'nsubjpass', 'csubjpass']

        token = spacy_tree
        token_head = spacy_tree

        while True:
            # try:
            #     head = token.head
            # except AttributeError:
            #     root, node_set

            if (token_head.dep_ in upwards and token_head.head != token):
                token_head = token_head.head

                for child in token_head.children:
                    if child.dep_ in subs:
                        node_set.append(child.dep_ )
                    # if child.dep_ in ['dobj','iobj','pobj']:
                    #     node_set.append(child.dep_ )
            else:
                break


        token = spacy_tree
        token_head = spacy_tree

        # print(root, node_set, ", ".join([str(child) for child in spacy_tree.children]))

        while True:

            if (token_head.dep_ in upwards and token_head.head != token_head):
                token_head = token_head.head

                needs_loop = True
                while needs_loop:
                    # print("restart")

                    changed = False
                    children_list = token_head.children[:]
                    for i in range(0, len(children_list)):

                        # print(i, len(children_list), len(token_head.children))

                        if token_head.children[i].dep_ in subs:
                            # token_head.children[i].dep_ in ['dobj','iobj','pobj']:
                            token.children.append(token_head.children[i])
                            token_head.children.pop(i)
                            changed = True
                            break

                    if not changed:
                        needs_loop = False
                        # print("finish")

            else:
                break

        # print(root, node_set, ", ".join([str(child) for child in spacy_tree.children]))

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