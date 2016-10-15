from nltk import Tree
from types import FunctionType
from internallib.dependency_helpers import *
from internallib.rule_applier import *
from internallib.tree_utils import find_in_spacynode
import inspect
from functools import wraps

class Obj(RuleApplier):
    def __init__(self):
        RuleApplier.__init__(self)
        self.tags_to_be_removed = set(['punct', 'appos', 'det', ' ', ''])
        return

    @RuleApplier.register_function
    def remove_duplicates(self, root, node_set, spacy_tree):
        """
            1) This groups sentence with e.g.: multiple "punct" into the same group for easier analysis.
        """
        return root, set(node_set), spacy_tree, False

    @RuleApplier.register_function
    def remove_tags(self, root, node_set, spacy_tree):
        """1) Consider the following sentence:
            "2 Related work Learning to rank has been a promising research area which continuously improves web search relevance (Burges et al."

            The dependency parser puts not the action the improves something as a parent of the word "improves" in the in the tree, and adds to it the relcl relation.
            This method adjusts the tree, bringing the node above under "improves".

            2) Consider the following sentence:
            "Evaluation on the ACE 2003 corpus shows that, compared with a baseline coreference resolution system of no explicit anaphoricity determination, their method improves the performance by 2.8, 2.2 and 4.5 to 54.5, 64.0 and 60.8 in F1-measure (due to the gain in precision) on the NWIRE, NPAPER and BNEWS domains, respectively, via careful determination of an anaphoricity threshold with proper constraint-based representation and global optimization."
            "Adding latent states to the smoothing model further improves the POS tagging accuracy (Huang and Yates, 2012)."
            
            The "appos" relation prints further information on the noun that is part of the "obj" node. http://universaldependencies.org/u/dep/appos.html
            One can remove it as in all observed cases the extra information wasn't really relevant (wither it were citations, or long subsequent clauses)
        """

        isApplied = False

        # print("END   Obj", self.tags_to_be_removed, root, node_set, spacy_tree)

        node_set = set(node_set) - self.tags_to_be_removed

        for child in spacy_tree.children:
            if child.dep_ in self.tags_to_be_removed:
                isApplied = True
                child.nofollow = True

        # print("END   Obj", self.tags_to_be_removed, root, node_set, spacy_tree)

        return root, node_set, spacy_tree, isApplied

    @RuleApplier.register_function
    def tranform_tags(self, root, node_set, spacy_tree):
        """
            1) This transform tags from several variations into a more general version. The mappings are contained
            in the self.translation_rules variables.
        """

        node_set = set([self.rewrite_dp_tag(node) for node in node_set])
        return root, node_set, spacy_tree, False

    @RuleApplier.register_function
    def remove_after_comma_prep(self, root, node_set, spacy_tree):
        """1) Consider the following sentence:
            "DoppelÃ¢Â€Â™s optimization is orthogonal to BCC: Doppel improves performance when ww dependencies happen, while BCC avoids false aborts caused by rw dependencies."
            "Their results show that the feature improves the parsing performance, which coincides with our analysis in Section 1.1."

            One can stop printing the "obj" after ", which" or ", while".
        """

        isApplied = False

        while_ = find_in_spacynode(spacy_tree, "", "while")
        which_ = find_in_spacynode(spacy_tree, "", "which")
        comma_ = find_in_spacynode(spacy_tree, "", ",")

        if (which_ != False and comma_ != False and (which_.idx - comma_.idx) == 2):
            isApplied = True
            comma_.nofollow = True
            which_.head.nofollow = True

        if (while_ != False and comma_ != False and (while_.idx - comma_.idx) == 2):
            isApplied = True
            comma_.nofollow = True
            while_.head.nofollow = True

        return root, node_set, spacy_tree, isApplied

    @RuleApplier.register_function
    def break_into_multiple_relations(self, root, node_set, spacy_tree):
        """1) TODO - Consider the following sentence:
            "The spirit of this work more closely resembles that of Finkel and Manning (2009) , which improves both parsing and named entity recognition by combining the two tasks."

            It should yield 2 relations as it improves "parsing" AND "named entity recognition"
        """

        return root, node_set, spacy_tree, False


class Subj(RuleApplier):
    def __init__(self):
        RuleApplier.__init__(self)
        self.tags_to_be_removed = set(['punct', 'appos', 'det', ' ', ''])
        return

    @RuleApplier.register_function
    def remove_duplicates(self, root, node_set, spacy_tree):
        """
            1) This groups sentence with e.g.: multiple "punct" into the same group for easier analysis.
        """
        return root, set(node_set), spacy_tree, False

    @RuleApplier.register_function
    def remove_tags(self, root, node_set, spacy_tree):
        """1) Consider the following sentence:
            "In this way, we can show that the bidirectional model improves alignment quality and enables the extraction of more correct phrase pairs."

            It is clear that the rule could simply yield "bidirectional model" instead of "the bidirectional model".

            2) Consider the following sentence:
            "LSB [19] is the first LSH method that is designed for disk-resident data, followed by C2LSH [4], which improves the efficiency and accuracy and reduces the space requirement."
            
            The "appos" relation prints further information on the noun that is part of the "obj" node. http://universaldependencies.org/u/dep/appos.html
            One can remove it as in all observed cases the extra information wasn't really relevant "[4]".
        """

        isApplied = False

        node_set = set(node_set) - self.tags_to_be_removed

        for child in spacy_tree.children:
            if child.dep_ in self.tags_to_be_removed:
                isApplied = True
                child.nofollow = True

        # print("END   Obj", self.tags_to_be_removed, root, node_set, spacy_tree)

        return root, node_set, spacy_tree, isApplied

    @RuleApplier.register_function
    def tranform_tags(self, root, node_set, spacy_tree):
        """
            1) This transform tags from several variations into a more general version. The mappings are contained
            in the self.translation_rules variables.
        """
        node_set = set([self.rewrite_dp_tag(node) for node in node_set])
        return root, node_set, spacy_tree, False

    @RuleApplier.register_function
    def remove_advcl(self, root, node_set, spacy_tree):
        """
            1) Consider the following sentence:
            "Approaches that do not explicitly involve resource adaptation include Wan (2009), which uses co-training (Blum and Mitchell, 1998) with English vs. Chinese features comprising the two independent Ã¢Â€Â•viewsÃ¢Â€Â– to exploit unlabeled Chinese data and a labeled English corpus and thereby improves Chinese sentiment classification."
            
            Shouldn't follow advcl.


            2) TODO - now consider:
            "Two algorithms, BNL and DC are proposed in [4], while SFS [5], is based on the same principle as BNL, but improves performance by first sorting the data according to a monotone function."
            
            subj should only be "Two algorithms, BNL and DC", thus the relcl should not be followed.
        """

        isApplied = False

        advcl_ = find_in_spacynode(spacy_tree, "advcl", "")

        if advcl_ != False:
            isApplied = True
            advcl_.nofollow = True

        return root, node_set, spacy_tree, isApplied

    @RuleApplier.register_function
    def remove_after_comma_prep(self, root, node_set, spacy_tree):
        """1) Consider the following sentence:
            "Harabagiu and Hickl (2006) recently demonstrated that textual entailment inference information, which in this system is a set of directional inference relations, improves the performance of a QA system significantly even without using any other form of semantic inference."
            
            One can stop printing the "obj" after ", which"
        """

        isApplied = False

        while_ = find_in_spacynode(spacy_tree, "", "while")
        which_ = find_in_spacynode(spacy_tree, "", "which")
        comma_ = find_in_spacynode(spacy_tree, "", ",")

        if (which_ != False and comma_ != False and (which_.idx - comma_.idx) == 2):
            isApplied = True
            comma_.nofollow = True
            which_.head.nofollow = True

        if (while_ != False and comma_ != False and (while_.idx - comma_.idx) == 2):
            isApplied = True
            comma_.nofollow = True
            while_.head.nofollow = True

        return root, node_set, spacy_tree, isApplied

    @RuleApplier.register_function
    def break_into_multiple_relations(self, root, node_set, spacy_tree):
        """1) TODO: Consider the following sentence:
            "Using textual entailment output (Stern and Dagan, 2011) and embedding-based representations (Iyyer et al., 2014) further improves the result."

            Should yield 2 subjs such as "Using textual entailment output (Stern and Dagan, 2011)" AND "embedding-based representations (Iyyer et al., 2014)"
        """

        return root, node_set, spacy_tree, False


class ProcessChildren(object):
    def __init__(self):
        self.obj = Obj()
        self.subj = Subj()
        return

    def applyAll(self, nltk_tree_obj, nltk_tree_subj, spacy_tree):
        nltk_tree_obj, applied_obj = self.obj.apply(nltk_tree_obj, spacy_tree, tree_root="obj")
        nltk_tree_subj, applied_subj = self.subj.apply(nltk_tree_subj, spacy_tree, tree_root="subj")
        return nltk_tree_obj, nltk_tree_subj, (applied_obj + applied_subj)