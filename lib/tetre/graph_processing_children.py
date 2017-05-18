# from tetre.dependency_helpers import *
from tetre.rule_applier import *
from tree_utils import find_in_spacynode

class Children(RuleApplier):
    def __init__(self):
        RuleApplier.__init__(self)
        self.tags_to_be_removed = set(['det', ' ', ''])
        return

    def bring_grandchild_prep_or_relcl_up_as_child(self, root, node_set, spacy_tree):
        """
            1) Consider the following sentence:
            "Experiments show that the proposed method improves the performance by 2.9 and 1.6 to 67.3 and 67.2 in F1-measure on the MUC-6 and MUC-7 corpora, respectively, due to much more gain in precision compared with the loss in recall."

            The dependency parser relates the "prep by" relationship to "performance" instead of "improves", causing the dobj part to be too large.

            2) Now consider:
            "(Taskar et al., 2004) suggested a method for maximal margin parsing which employs the dynamic programming approach to decoding and parameter estimation problems."

            This would also bring up prep "to".

            3) Now consider:
            "One method considers the phrases as bag-ofwords and employs a convolution model to transform the word embeddings to phrase embeddings (Collobert et al."
            "(Kobayashi et al., 2004) employs an iterative semi-automatic approach which requires human input at every iteration."
            "The formers precision on the explicit feature extraction task is 22% lower than OPINE s while the latter employs an iterative semi-automatic approach which requires significant human input; neither handles implicit features."

            This would also bring up "relcl".

            4) Now consider:
            "It employs a single coherence model based on semantic signatures similar to our coherence objective."

            This would also bring up "acl".

            5) Now consider:
            "The algorithm employs a max-heap H for managing combinations of feature entries in descending order of their combination scores."

            This would also bring up prep "for".

            6) Now consider:
            "SemTag uses the TAP knowledge base5 , and employs the cosine similarity with TF-IDF weighting scheme to compute the match degree between a mention and an entity, achieving an accuracy of around 82%."

            This would also bring up prep "with".

            7) Now consider:
            "QPipe employs a micro-kernel approach whereby functionality of each physical operator is exposed as a separate service."

            This would also bring up prep "whereby".
        """

        bring_up = [
            ("relcl", "", "mod"),
            ("acl", "", "mod"),
            ("advcl", "", "mod"),
            ("prep", "by", "prep"),
            ("prep", "to", "prep"),
            ("prep", "for", "prep"),
            ("prep", "with", "prep"),
            ("prep", "whereby", "prep"),
        ]

        isApplied = False

        node = spacy_tree
        head = spacy_tree.head

        for dep_, orth_, dep_new_ in bring_up:

            # print ("0", dep_, orth_, dep_new_)
        
            changed = True
            while changed:
                changed = False

                prep = find_in_spacynode(node, dep_, orth_)
                if prep == False:
                    break

                # print ("1", prep.dep_, prep.orth_, prep.idx)

                prep_head = prep.head.children[:]

                for i in range(0, len(prep_head)):

                    # print ("2", prep_head[i].dep_, prep_head[i].orth_, prep_head[i].idx)

                    if prep.dep_ in prep_head[i].dep_ and \
                        prep.orth_ == prep_head[i].orth_ and \
                        prep.idx == prep_head[i].idx:

                        isApplied = True

                        #adjust actual tree
                        prep.head.children.pop(i)
                        head.children.append(prep)
                        prep.head = head
                        prep.dep_ = dep_new_

                        #adjust representation
                        node_set = list(node_set)
                        node_set.append(dep_new_)

                        changed = True
                        break

        return root, node_set, spacy_tree, isApplied

class Obj(Children):
    def __init__(self):
        Children.__init__(self)
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

    # @RuleApplier.register_function
    # def remove_after_comma_prep(self, root, node_set, spacy_tree):
    #     """1) Consider the following sentence:
    #         "Doppels optimization is orthogonal to BCC: Doppel improves performance when ww dependencies happen, while BCC avoids false aborts caused by rw dependencies."
    #         "Their results show that the feature improves the parsing performance, which coincides with our analysis in Section 1.1."

    #         One can stop printing the "obj" after ", which" or ", while".
    #     """

    #     isApplied = False

    #     while_ = find_in_spacynode(spacy_tree, "", "while")
    #     which_ = find_in_spacynode(spacy_tree, "", "which")
    #     comma_ = find_in_spacynode(spacy_tree, "", ",")

    #     if (which_ != False and comma_ != False and (which_.idx - comma_.idx) == 2):
    #         isApplied = True
    #         comma_.nofollow = True
    #         which_.head.nofollow = True

    #     if (while_ != False and comma_ != False and (while_.idx - comma_.idx) == 2):
    #         isApplied = True
    #         comma_.nofollow = True
    #         while_.head.nofollow = True

    #     return root, node_set, spacy_tree, isApplied

    @RuleApplier.register_function
    def bring_grandchild_prep_or_relcl_up_as_child(self, root, node_set, spacy_tree):
        return super(Obj, self).bring_grandchild_prep_or_relcl_up_as_child(root, node_set, spacy_tree)



class Subj(Children):
    def __init__(self):
        Children.__init__(self)
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

    # @RuleApplier.register_function
    # def remove_advcl(self, root, node_set, spacy_tree):
    #     """
    #         1) Consider the following sentence:
    #         "Approaches that do not explicitly involve resource adaptation include Wan (2009), which uses co-training (Blum and Mitchell, 1998) with English vs. Chinese features comprising the two independent views to exploit unlabeled Chinese data and a labeled English corpus and thereby improves Chinese sentiment classification."
            
    #         Shouldn't follow advcl.


    #         2) TODO - now consider:
    #         "Two algorithms, BNL and DC are proposed in [4], while SFS [5], is based on the same principle as BNL, but improves performance by first sorting the data according to a monotone function."
            
    #         subj should only be "Two algorithms, BNL and DC", thus the relcl should not be followed.
    #     """

    #     isApplied = False

    #     advcl_ = find_in_spacynode(spacy_tree, "advcl", "")

    #     if advcl_ != False:
    #         isApplied = True
    #         advcl_.nofollow = True

    #     return root, node_set, spacy_tree, isApplied

    # @RuleApplier.register_function
    # def remove_after_comma_prep(self, root, node_set, spacy_tree):
    #     """1) Consider the following sentence:
    #         "Harabagiu and Hickl (2006) recently demonstrated that textual entailment inference information, which in this system is a set of directional inference relations, improves the performance of a QA system significantly even without using any other form of semantic inference."
            
    #         One can stop printing the "obj" after ", which"
    #     """

    #     isApplied = False

    #     while_ = find_in_spacynode(spacy_tree, "", "while")
    #     which_ = find_in_spacynode(spacy_tree, "", "which")
    #     comma_ = find_in_spacynode(spacy_tree, "", ",")

    #     if (which_ != False and comma_ != False and (which_.idx - comma_.idx) == 2):
    #         isApplied = True
    #         comma_.nofollow = True
    #         which_.head.nofollow = True

    #     if (while_ != False and comma_ != False and (while_.idx - comma_.idx) == 2):
    #         isApplied = True
    #         comma_.nofollow = True
    #         while_.head.nofollow = True

    #     return root, node_set, spacy_tree, isApplied

    @RuleApplier.register_function
    def bring_grandchild_prep_or_relcl_up_as_child(self, root, node_set, spacy_tree):
        return super(Subj, self).bring_grandchild_prep_or_relcl_up_as_child(root, node_set, spacy_tree)

class ProcessChildren(object):
    def __init__(self):
        self.obj = Obj()
        self.subj = Subj()
        return

    def applyAll(self, nltk_tree_obj, nltk_tree_subj, spacy_tree):
        nltk_tree_obj, applied_obj = self.obj.apply(nltk_tree_obj, spacy_tree, tree_root="obj")
        nltk_tree_subj, applied_subj = self.subj.apply(nltk_tree_subj, spacy_tree, tree_root="subj")
        return nltk_tree_obj, nltk_tree_subj, (applied_obj + applied_subj)