from nltk import Tree
from types import FunctionType
from internallib.dependency_helpers import *
from internallib.rule_applier import *
from internallib.tree_utils import find_in_spacynode
import inspect
from functools import wraps
import sys

class Growth(RuleApplier):
    def __init__(self):
        RuleApplier.__init__(self)
        self.subs = ['nsubj', 'csubj', 'nsubjpass', 'csubjpass']
        self.move_if = [("xcomp", "obj"), ("ccomp", "obj")]
        self.downwards_subj = "nsubj"

    @RuleApplier.register_function
    def replace_on_relcl(self, root, node_set, spacy_tree):
        """
            1) Consider the following sentence:
            "2 Related work Learning to rank has been a promising research area which continuously improves web search relevance (Burges et al."

            The dependency parser puts not the action the improves something as a parent of the word "improves" in the in the tree, and adds to it the relcl relation.
            This method adjusts the tree, bringing the node above under "improves".


            2) Consider the following sentence:
            "The best known recovery algorithm for dirty mapping entries, proposed in LazyFTL, exhibits two shortcomings that GeckoFTL improves upon."

            In this case, GeckoFTL is is a proper noun, so it shouldn't be replaced.
        """

        upwards = ["relcl"]

        #adjust representation
        # has_subj = False
        # token = spacy_tree
        # token_head = spacy_tree

        # for node in node_set:
        #     if node in self.subs:
        #         has_subj = True

        # if (token_head.dep_ in upwards and token_head.head != token):
        #     if not has_subj:
        #         node_set.append(downwards)

        #adjust tree
        token = spacy_tree
        token_head = spacy_tree

        # print("0", token.to_tree_string())
        # print("0", token_head.to_tree_string())
        # print("0", token_head.to_tree_string())

        if (token_head.dep_ in upwards and token_head.head != token):
            token_head = token_head.head

            # print("1", token.to_tree_string())
            # print("1", token_head.to_tree_string())

            isChanging = False

            children_list = token.children[:]
            for i in range(0, len(children_list)):
                if (children_list[i].dep_ in self.subs):
                    if not (token.children[i].pos_ in ["NOUN","PROPN"]):
                        token.children.pop(i)
                        isChanging = True

            # print("2", token.to_tree_string())
            # print("2", token_head.to_tree_string())

            if (isChanging):
                children_list = token_head.children[:]
                for i in range(0, len(children_list)):
                    if (children_list[i].idx == token.idx):
                        token_head.children.pop(i)

                        #adjust representation
                        node_set.append(self.downwards_subj)

                # print("3", token.to_tree_string())
                # print("3", token_head.to_tree_string())

                # print("---------------")

                token_head.dep_ = self.downwards_subj
                token.children.append(token_head)
                token_head.head = token

        return root, node_set, spacy_tree

    @RuleApplier.register_function
    def recurse_on_conj_if_no_subj(self, root, node_set, spacy_tree):
        """
            1) Consider the following sentence:
            "Using many ASR hypotheses helps recover the ASR errors of NE words in 1-best ASR results and improves NER accuracy."

            The dependency parser puts not the action the improves something as a parent of the word "improves" in the in the tree, and adds to it the conj relation.
            This method adjusts the tree, bringing the node above under "improves".

            
            2) Now consider the following sentence:
            "Both identify product features from reviews, but OPINE significantly improves on both."

            Note how, although improves is a conj, "Both" is the subj up the tree. However, there is a "but" as the "cc", and beucase of this we need to pick the "conj" below instead of the "subj".
        """

        upwards = ["conj"]

        token = spacy_tree
        token_head = spacy_tree

        while True:

            if (token_head.dep_ in upwards        \
                and token_head.head != token_head \
                and len([child for child in token.children if child.dep_ in self.subs]) == 0):
                token_head = token_head.head

                needs_loop = True
                while needs_loop:

                    changed = False
                    children_list = token_head.children[:]

                    isBut = False
                    for j in range(0, len(children_list)):
                        if token_head.children[j].dep_ in "cc" \
                            and token_head.children[j].orth_ == "but":
                            isBut = True

                    for i in range(0, len(children_list)):
                        if  (not isBut and token_head.children[i].dep_ in self.subs) or \
                            (isBut and token_head.children[i].dep_ in "conj" and token_head.children[i] != token):

                            # print("1", token.to_tree_string())
                            # print("1", token_head.to_tree_string())
                            # print("1", node_set)
                            # print("1", isBut)

                            if isBut:
                                token_head.children[i].dep_ = self.downwards_subj

                            # adjust representation
                            node_set.append(token_head.children[i].dep_ )

                            #adjust actual tree
                            token.children.append(token_head.children[i])
                            token_head.children[i].head = token
                            token_head.children.pop(i)

                            # print("2", token.to_tree_string())
                            # print("2", token_head.to_tree_string())
                            # print("2", node_set)
                            # print("2", isBut)

                            # print("---------------")
                            # print()

                            changed = True
                            break

                    if not changed:
                        needs_loop = False

            else:
                break

        return root, node_set, spacy_tree

    @RuleApplier.register_function
    def bring_prep_by_up(self, root, node_set, spacy_tree):
        """
            1) Consider the following sentence:
            "Experiments show that the proposed method improves the performance by 2.9 and 1.6 to 67.3 and 67.2 in F1-measure on the MUC-6 and MUC-7 corpora, respectively, due to much more gain in precision compared with the loss in recall."

            The dependency parser relates the "prep by" relationship to "performance" instead of "improves", causing the dobj part to be too large.
        """

        obj = next((child for child in spacy_tree.children if "obj" in child.dep_), None)

        if obj != None:
            
            changed = True
            while changed:
                changed = False

                prep = find_in_spacynode(obj, "prep", "by")
                if prep == False:
                    break

                prep_head = prep.head.children[:]

                for i in range(0, len(prep_head)):
                    if "prep" in prep_head[i].dep_ and \
                        "by" == prep_head[i].orth_:

                        #adjust actual tree
                        prep.head.children.pop(i)
                        spacy_tree.children.append(prep)
                        prep.head = spacy_tree

                        #adjust representation
                        node_set.append("prep")

                        changed = True
                        break

        return root, node_set, spacy_tree

    @RuleApplier.register_function
    def transform_xcomp_if_no_dobj_tag(self, root, node_set, spacy_tree):
        """
            1) Consider the sentence:
            xcomp > "Recent work has showed that structured retrieval improves answer ranking for factoid questions: Bilotti et al."
            ccomp > "The Fat-Btree structure presented in [19] vastly reduces the index-modification cost and improves the dynamic data skew handling method."

            Although it is possible to understand that "structured retrieval" "improves" "answer ranking..." the "answer ranking..." part is
            not presented as a dobj dependency, but a xcomp dependency instead. This rule transforms xcomp into "obj" as both contain the same
            purpose for information extraction.
        """
        for replace, target in self.move_if:
            is_obj = False
            for child in spacy_tree.children:
                if target in child.dep_:
                    is_obj = True

            for child in spacy_tree.children:
                if replace in child.dep_:
                    if not is_obj:
                        child.dep_ = target
                        node_set = [target if node==replace else node for node in node_set]

        node_set = set([self.rewrite_dp_tag(node) for node in node_set])
        return root, node_set, spacy_tree

    @RuleApplier.register_function
    def bring_prep_in_up(self, root, node_set, spacy_tree):
        """
            1) TODO - Consider the following sentence:
            "While matrix factorization is widely used in recommender systems, matrix co-factorization helps to handle multiple aspects of the data and improves in predicting individual decisions (Hong et al. "

            One can see that "matrix co-factorization" and improves "predicting individual decisions". It could be rewriting as "improves prediction of individual decisions". Thus anything after a "prep in" could be considered an "obj".
        """

        target = "obj"
        replace = "prep"

        is_obj = False
        for child in spacy_tree.children:
            if target in child.dep_:
                is_obj = True

        for child in spacy_tree.children:
            if replace in child.dep_ and child.orth_ == "in":
                if not is_obj:
                    child.dep_ = target
                    node_set = [target if node==replace else node for node in node_set]

        node_set = set([self.rewrite_dp_tag(node) for node in node_set])
        return root, node_set, spacy_tree

    @RuleApplier.register_function
    def yield_multiple(self, root, node_set, spacy_tree):
        """
            1) TODO - Consider the following sentence:
            "ED-Join improves AllPairs-Ed using location-based and content-based mismatch filter by decreasing the number of grams."

            Ideally we would yield:
                "ED-Join"   "improves"  "AllPairs-Ed using location-based mismatch filter"
                "ED-Join"   "improves"  "AllPairs-Ed using content-based mismatch filter"
            Both with "prep" "by decreasing the number of grams"
        """

        return root, node_set, spacy_tree


class Reduction(RuleApplier):
    def __init__(self):
        RuleApplier.__init__(self)
        self.tags_to_be_removed = set(['punct', 'mark', ' ', ''])

    @RuleApplier.register_function
    def remove_duplicates(self, root, node_set, spacy_tree):
        """
            1) This groups sentence with e.g.: multiple "punct" into the same group for easier analysis.
        """
        return root, set(node_set), spacy_tree

    @RuleApplier.register_function
    def remove_tags(self, root, node_set, spacy_tree):
        """
            1) This removes dependency paths of the types contained in self.tags_to_be_removed as they are not considered
            relevant. This reduces the number of different groups.
        """

        node_set = set(node_set) - self.tags_to_be_removed

        for child in spacy_tree.children:
            if child.dep_ in self.tags_to_be_removed:
                child.nofollow = True

        return root, node_set, spacy_tree

    @RuleApplier.register_function
    def tranform_tags(self, root, node_set, spacy_tree):
        """
            1) This transform tags from several variations into a more general version. The mappings are contained
            in the self.translation_rules variables.
        """
        node_set = set([self.rewrite_dp_tag(node) for node in node_set])
        return root, node_set, spacy_tree

    @RuleApplier.register_function
    def yield_multiple(self, root, node_set, spacy_tree):
        """
            1) TODO - Unify multiple subj and fix representation:
            "Another partitional method ORCLUS [2] improves PROCLUS by selecting principal components so that clusters not parallel to the original dimensions can also be detected."

            It has 2 nsubj: "Another partitional method" and "ORCLUS [2]". They should be in the same sentence.
            Because it has 2 subj, the representation ends up being the one from the last nsubj.
        """

        return root, node_set, spacy_tree

class Process(object):
    def __init__(self):
        self.growth = Growth()
        self.reduction = Reduction()
        return

    def applyAll(self, nltk_tree, spacy_tree):

        # print("will process")

        nltk_tree = self.growth.apply(nltk_tree, spacy_tree)
        nltk_tree = self.reduction.apply(nltk_tree, spacy_tree)
        return nltk_tree