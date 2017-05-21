# from tetre.dependency_helpers import *
from tetre.rule_applier import *
from tree_utils import find_in_spacynode


class Children(RuleApplier):
    def __init__(self):
        RuleApplier.__init__(self)
        self.tags_to_be_removed = {'det', ' ', ''}
        return

    def bring_grandchild_prep_or_relcl_up_as_child(self, root, node_set, spacy_tree):
        """
            1) Consider the following sentence:
            "Experiments show that the proposed method improves the performance by 2.9 and 1.6 to 67.3 and 67.2
            in F1-measure on the MUC-6 and MUC-7 corpora, respectively, due to much more gain in precision compared
            with the loss in recall."

            In this case, The dependency parser relates the "prep by" relationship to "performance" instead of
            "improves", causing the dobj part to be too large.


            2) Now consider the following sentence:
            "(Taskar et al., 2004) suggested a method for maximal margin parsing which employs the dynamic
            programming approach to decoding and parameter estimation problems."

            In this case, this would also bring up prep "to".


            3) Now consider the following sentences:
            "One method considers the phrases as bag-ofwords and employs a convolution model to transform the word
            embeddings to phrase embeddings (Collobert et al."
            "(Kobayashi et al., 2004) employs an iterative semi-automatic approach which requires human input at every
            iteration."
            "The formers precision on the explicit feature extraction task is 22% lower than OPINE s while the latter
            employs an iterative semi-automatic approach which requires significant human input; neither handles
            implicit features."

            In this case, this would also bring up "relcl".


            4) Now consider the following sentences:
            "It employs a single coherence model based on semantic signatures similar to our coherence objective."

            In this case, this would also bring up "acl".


            5) Now consider the following sentences:
            "The algorithm employs a max-heap H for managing combinations of feature entries in descending order of
            their combination scores."

            In this case, this would also bring up prep "for".


            6) Now consider the following sentences:
            "SemTag uses the TAP knowledge base5 , and employs the cosine similarity with TF-IDF weighting scheme
            to compute the match degree between a mention and an entity, achieving an accuracy of around 82%."

            In this case, this would also bring up prep "with".


            7) Now consider the following sentences:
            "QPipe employs a micro-kernel approach whereby functionality of each physical operator is exposed as
            a separate service."

            In this case, this would also bring up prep "whereby".
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

        is_applied = False

        node = spacy_tree
        head = spacy_tree.head

        for dep_, orth_, dep_new_ in bring_up:

            changed = True
            while changed:
                changed = False

                prep = find_in_spacynode(node, dep_, orth_)
                if not prep:
                    break

                prep_head = prep.head.children[:]

                for i in range(0, len(prep_head)):

                    if prep.dep_ in prep_head[i].dep_ and \
                                    prep.orth_ == prep_head[i].orth_ and \
                                    prep.idx == prep_head[i].idx:

                        is_applied = True

                        # adjust actual tree
                        prep.head.children.pop(i)
                        head.children.append(prep)
                        prep.head = head
                        prep.dep_ = dep_new_

                        # adjust representation
                        node_set = list(node_set)
                        node_set.append(dep_new_)

                        changed = True
                        break

        return root, node_set, spacy_tree, is_applied


class Obj(Children):
    def __init__(self):
        Children.__init__(self)
        return

    @RuleApplier.register_function
    def remove_duplicates(self, root, node_set, spacy_tree):
        """This groups sentence with e.g.: multiple "punct" into the same group for easier analysis.
        """
        return root, set(node_set), spacy_tree, False

    @RuleApplier.register_function
    def remove_tags(self, root, node_set, spacy_tree):
        """1) Consider the following sentence:
            "2 Related work Learning to rank has been a promising research area which continuously improves web
            search relevance (Burges et al."

            In this case, the dependency parser puts not the action the improves something as a parent of the word
            "improves" in the in the tree, and adds to it the relcl relation. This method adjusts the tree, bringing
            the node above under "improves".


            2) Now consider the following sentence:
            "Evaluation on the ACE 2003 corpus shows that, compared with a baseline coreference resolution system of
            no explicit anaphoricity determination, their method improves the performance by 2.8, 2.2 and 4.5 to 54.5,
            64.0 and 60.8 in F1-measure (due to the gain in precision) on the NWIRE, NPAPER and BNEWS domains,
            respectively, via careful determination of an anaphoricity threshold with proper constraint-based
            representation and global optimization."
            "Adding latent states to the smoothing model further improves the POS tagging accuracy (Huang and Yates,
            2012)."
            
            In this case, the "appos" relation prints further information on the noun that is part of the "obj" node.
            http://universaldependencies.org/u/dep/appos.html - one can remove it as in all observed cases the extra
            information wasn't really relevant (wither it were citations, or long subsequent clauses)
        """

        is_applied = False

        node_set = set(node_set) - self.tags_to_be_removed

        for child in spacy_tree.children:
            if child.dep_ in self.tags_to_be_removed:
                is_applied = True
                child.no_follow = True

        return root, node_set, spacy_tree, is_applied

    @RuleApplier.register_function
    def tranform_tags(self, root, node_set, spacy_tree):
        """This transform tags from several variations into a more general version. The mappings are contained
        in the self.translation_rules variables.
        """

        node_set = set([self.rewrite_dp_tag(node) for node in node_set])
        return root, node_set, spacy_tree, False

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
            "In this way, we can show that the bidirectional model improves alignment quality and enables the
            extraction of more correct phrase pairs."

            In this case, it is clear that the rule could simply yield "bidirectional model" instead of "the
            bidirectional model".


            2) Now consider the following sentences:
            "LSB [19] is the first LSH method that is designed for disk-resident data, followed by C2LSH
            [4], which improves the efficiency and accuracy and reduces the space requirement."
            
            In this case, the "appos" relation prints further information on the noun that is part of the "obj" node.
            http://universaldependencies.org/u/dep/appos.html - one can remove it as in all observed cases the extra
            information wasn't really relevant "[4]".
        """

        is_applied = False

        node_set = set(node_set) - self.tags_to_be_removed

        for child in spacy_tree.children:
            if child.dep_ in self.tags_to_be_removed:
                is_applied = True
                child.no_follow = True

        return root, node_set, spacy_tree, is_applied

    @RuleApplier.register_function
    def tranform_tags(self, root, node_set, spacy_tree):
        """This transform tags from several variations into a more general version. The mappings are contained
        in the self.translation_rules variables.
        """
        node_set = set([self.rewrite_dp_tag(node) for node in node_set])
        return root, node_set, spacy_tree, False

    @RuleApplier.register_function
    def bring_grandchild_prep_or_relcl_up_as_child(self, root, node_set, spacy_tree):
        return super(Subj, self).bring_grandchild_prep_or_relcl_up_as_child(root, node_set, spacy_tree)


class ProcessChildren(object):
    def __init__(self):
        self.obj = Obj()
        self.subj = Subj()
        return

    def apply_all(self, nltk_tree_obj, nltk_tree_subj, spacy_tree):
        nltk_tree_obj, applied_obj = self.obj.apply(nltk_tree_obj, spacy_tree, tree_root="obj")
        nltk_tree_subj, applied_subj = self.subj.apply(nltk_tree_subj, spacy_tree, tree_root="subj")
        return nltk_tree_obj, nltk_tree_subj, (applied_obj + applied_subj)
