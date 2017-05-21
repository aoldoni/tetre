from tetre.rule_applier import *
from tree_utils import find_in_spacynode, merge_nodes

from functools import reduce


class Growth(RuleApplier):
    def __init__(self):
        RuleApplier.__init__(self)
        self.subs = ['nsubj', 'csubj', 'nsubjpass', 'csubjpass']
        self.objs = ['dobj', 'iobj', 'pobj']
        self.move_if = [("xcomp", "obj"), ("ccomp", "obj"), ("xcomp", "subj"), ("ccomp", "subj")]
        self.downwards_subj = "nsubj"
        self.downwards_obj = "dobj"

    @RuleApplier.register_function
    def replace_subj_if_dep_is_relcl_or_ccomp(self, root, node_set, spacy_tree):
        """
            1) Consider the following sentence:
            "2 Related work Learning to rank has been a promising research area which continuously improves web
            search relevance (Burges et al."

            In this case, the dependency parser puts not the action the improves something as a parent of the word
            "improves" in the in the tree, and adds to it the relcl relation. This method adjusts the tree, bringing
            the node above under "improves".


            2) Now consider the following sentence:
            "The best known recovery algorithm for dirty mapping entries, proposed in LazyFTL, exhibits
            two shortcomings that GeckoFTL improves upon."

            In this case, GeckoFTL is is a proper noun, so it shouldn't be replaced.
        """

        is_applied = False

        upwards = ["relcl", "ccomp"]

        # adjust tree
        token = spacy_tree
        token_head = spacy_tree

        if token_head.dep_ in upwards and token_head.head != token:
            token_head = token_head.head

            is_changing_possibilities = []
            is_changing = False
            has_subj = False

            children_list = token.children[:]
            for i in range(0, len(children_list)):
                if children_list[i].dep_ in self.subs:
                    has_subj = True

                    if not (token.children[i].pos_ in ["NOUN", "PROPN", "VERB", "NUM", "PRON", "X"]):
                        token.children.pop(i)
                        is_changing_possibilities.append(True)
                    else:
                        is_changing_possibilities.append(False)

            if True in is_changing_possibilities:
                is_changing = True

            if not has_subj:
                is_changing = True

            if is_changing:
                is_applied = True
                children_list = token_head.children[:]
                for i in range(0, len(children_list)):
                    if children_list[i].idx == token.idx:
                        token_head.children.pop(i)

                        # adjust representation
                        node_set.append(self.downwards_subj)

                token_head.dep_ = self.downwards_subj
                token.children.append(token_head)
                token_head.head = token

        return root, node_set, spacy_tree, is_applied

    @RuleApplier.register_function
    def recurse_on_dep_conj_if_no_subj(self, root, node_set, spacy_tree):
        """
            1) Consider the following sentence:
            "Using many ASR hypotheses helps recover the ASR errors of NE words in 1-best ASR results and
            improves NER accuracy."

            In this case, the dependency parser puts not the action the improves something as a parent of the word
            "improves" in the in the tree, and adds to it the conj relation. This method adjusts the tree, bringing
            the node above under "improves".

            
            2) Now consider the following sentence:
            "Both identify product features from reviews, but OPINE significantly improves on both."

            In this case, note how although improves is a conj, "Both" is the subj up the tree. However, there is a
            "but" as the "cc", and beucase of this we need to pick the "conj" below instead of the "subj".


            3) Now consider the following sentence:
            "SFS [6] (sort-filter-skyline) is based on the same rationale as BNL , but improves performance by
            first sorting the data according to a monotone function."

            In this case, this has a "but", however no other conj, in this case we should use the nsubj again.


            4) Now consider the following sentence:
            "[16] studies the usage of grammars and LZ77 parsing for compression of similar sequence collections and
            improves complexity bounds with respect to space as well as time."

            In this case, the subj is actually the dobj of the head.
        """

        is_applied = False

        upwards = ["conj"]

        token = spacy_tree
        token_head = spacy_tree

        while True:

            if token_head.dep_ in upwards        \
                        and token_head.head != token_head \
                        and len([child for child in token.children if child.dep_ in self.subs]) == 0:

                token_head = token_head.head
                children_list = token_head.children[:]

                is_but = False
                other_conj_exists = False
                has_subj = False
                has_obj = False

                for j in range(0, len(children_list)):
                    if token_head.children[j].dep_ in "cc" \
                            and token_head.children[j].orth_ == "but":
                        is_but = True
                    if token_head.children[j].dep_ in "conj" \
                            and token_head.children[j] != token:
                        other_conj_exists = True
                    if "subj" in token_head.children[j].dep_:
                        has_subj = True
                    if "obj" in token_head.children[j].dep_:
                        has_obj = True

                for i in range(0, len(children_list)):
                    is_other_conj = token_head.children[i].dep_ == "conj" and token_head.children[i] != token
                    is_subj = token_head.children[i].dep_ in self.subs
                    is_obj = token_head.children[i].dep_ in self.objs

                    node_result = find_in_spacynode(token_head.children[i], token.dep_, token.orth_)

                    if node_result:
                        is_sub_child = True
                    else:
                        is_sub_child = False

                    cond_subj = not is_but and is_subj
                    cond_dobj = not is_but and not has_subj and is_obj
                    cond_conj_other = is_but and not is_subj and other_conj_exists and \
                                      is_other_conj and not is_sub_child
                    cond_conj_same = is_but and not other_conj_exists and is_subj

                    if cond_subj or \
                            cond_conj_other or \
                            cond_dobj or \
                            cond_conj_same:

                        is_applied = True

                        if cond_dobj or cond_conj_other:
                            token_head.children[i].dep_ = self.downwards_subj

                        # adjust representation
                        node_set.append(token_head.children[i].dep_)

                        # adjust actual tree
                        token.children.append(token_head.children[i])
                        token_head.children[i].head = token
                        token_head.children.pop(i)

                        break

            else:
                break

        return root, node_set, spacy_tree, is_applied

    @RuleApplier.register_function
    def transform_xcomp_to_dobj_or_sub_if_doesnt_exists(self, root, node_set, spacy_tree):
        """
            1) Consider the sentences:
            -- xcomp > "Recent work has showed that structured retrieval improves answer ranking for factoid
            questions: Bilotti et al."
            -- ccomp > "The Fat-Btree structure presented in [19] vastly reduces the index-modification cost
            and improves the dynamic data skew handling method."

            In this case, although it is possible to understand that "structured retrieval" "improves"
            "answer ranking..." the "answer ranking..." part is not presented as a dobj dependency, but a xcomp
            dependency instead. This rule transforms xcomp into "obj" as both contain the same purpose for information
            extraction.


            2) Now consider the following sentence:
            -- ccomp > "2 Related Work Caching frequently accessed data at the client side not only improves the
            userÃ¢Â€Â™s experience of the distributed system, but also alleviates the serverÃ¢Â€Â™s workload and
            enhances its scalability."

            In this case, although in this sentence the dobj was detected, the ccomp is the nsubj. Thus, after
            replacing the items for dobj, if there is no nsubj in the sentence we try to tranform then in nsubj.
        """

        is_applied = False

        for replace, target in self.move_if:
            is_obj = False

            for child in spacy_tree.children:
                if target in child.dep_:
                    is_obj = True
                    break

            if is_obj:
                continue

            for child in spacy_tree.children:
                if replace in child.dep_:
                    is_applied = True

                    child.dep_ = target
                    node_set = [target if node == replace else node for node in node_set]
                    break

        node_set = set([self.rewrite_dp_tag(node) for node in node_set])
        return root, node_set, spacy_tree, is_applied

    @RuleApplier.register_function
    def transform_prep_in_to_dobj(self, root, node_set, spacy_tree):
        """
            1) Consider the following sentence:
            "While matrix factorization is widely used in recommender systems, matrix co-factorization helps to handle
            multiple aspects of the data and improves in predicting individual decisions (Hong et al. "

            In this case, one can see that "matrix co-factorization" and improves "predicting individual decisions". It
            could be rewriting as "improves prediction of individual decisions". Thus anything after a "prep in"
            could be considered an "obj".
        """
        is_applied = False

        target = "obj"
        replace = "prep"

        is_obj = False
        for child in spacy_tree.children:
            if target in child.dep_:
                is_obj = True

        for child in spacy_tree.children:
            if replace in child.dep_ and child.orth_ == "in":
                if not is_obj:
                    is_applied = True

                    child.dep_ = target
                    node_set = [target if node == replace else node for node in node_set]

        node_set = list(set([self.rewrite_dp_tag(node) for node in node_set]))
        return root, node_set, spacy_tree, is_applied

    @RuleApplier.register_function
    def add_dobj_if_dep_is_subj(self, root, node_set, spacy_tree):
        """
            1) Consider the following sentence:
            "Turney (2005) extends the above approach by introducing the latent relational analysis (LRA), which uses
            automatically generated synonyms, learns suitable patterns, and performs singular value decomposition
            in order to smooth the frequencies."
            "This work uses materialized views to further benefit from commonalities across queries."

            In the first sentence, the relation uses(which; automatically generated synonyms) could have been extracted
            by getting the nsubj dependency and transforming it to be the child's dobj. The same is valid for the
            second example.
        """
        token = spacy_tree
        token_head = token.head

        is_applied = False
        has_subj = False
        has_obj = False

        for j in range(0, len(token.children)):
            if "subj" in token.children[j].dep_:
                has_subj = True
            if "obj" in token.children[j].dep_:
                has_obj = True

        if "subj" in token.dep_ and has_subj and not has_obj:
            is_applied = True
            
            children_list = token_head.children[:]

            for i in range(0, len(children_list)):
                if children_list[i].idx == token.idx:
                    token_head.children.pop(i)

                    # adjust representation
                    node_set.append(self.downwards_obj)

            token_head.dep_ = self.downwards_obj
            token.children.append(token_head)
            token_head.head = token

        return root, node_set, spacy_tree, is_applied


class Reduction(RuleApplier):
    def __init__(self):
        RuleApplier.__init__(self)
        self.tags_to_be_removed = {'punct', 'mark', ' ', '', 'meta'}

    @RuleApplier.register_function
    def remove_duplicates(self, root, node_set, spacy_tree):
        """This groups sentence with e.g.: multiple "punct" into the same group for easier analysis.
        """
        return root, set(node_set), spacy_tree, False

    @RuleApplier.register_function
    def remove_tags(self, root, node_set, spacy_tree):
        """This removes dependency paths of the types contained in self.tags_to_be_removed as they are not considered
        relevant. This reduces the number of different groups.
        """
        is_applied = False

        node_set = set(node_set) - self.tags_to_be_removed

        for child in spacy_tree.children:
            if child.dep_ in self.tags_to_be_removed:
                is_applied = True
                child.no_follow = True

        return root, node_set, spacy_tree, is_applied

    @RuleApplier.register_function
    def transform_tags(self, root, node_set, spacy_tree):
        """This transform tags from several variations into a more general version. The mappings are contained
        in the self.translation_rules variables.
        """
        node_set = set([self.rewrite_dp_tag(node) for node in node_set])
        return root, node_set, spacy_tree, False

    @RuleApplier.register_function
    def merge_multiple_subj_or_dobj(self, root, node_set, spacy_tree):
        """This intends to unify multiple subj and fix representation. Consider the following sentence:
            "Another partitional method ORCLUS [2] improves PROCLUS by selecting principal components so that clusters
            not parallel to the original dimensions can also be detected."

            In this example, the sentence has 2 nsubj: "Another partitional method" and "ORCLUS [2]". They should
            be in the same sentence. Because it has 2 subj, the representation ends up being the one from the
            last nsubj.
        """

        is_applied = False
        groups = ["subj", "obj"]
        
        for group in groups:
            this_group = []
            count = reduce(lambda x, y: x + 1 if group in y.dep_ else x, spacy_tree.children, 0)

            if count < 2:
                continue

            changed = True
            while changed:
                changed = False
                children_list = spacy_tree.children[:]

                for i in range(0, len(children_list)):
                    if group in children_list[i].dep_:
                        this_group.append(children_list[i])
                        spacy_tree.children.pop(i)

                        is_applied = True
                        changed = True
                        break

            child = merge_nodes(this_group)
            spacy_tree.children.append(child)
            child.head = spacy_tree

        return root, node_set, spacy_tree, is_applied


class Process(object):
    def __init__(self):
        self.growth = Growth()
        self.reduction = Reduction()
        return

    def apply_all(self, nltk_tree, spacy_tree):

        nltk_tree, applied_growth = self.growth.apply(nltk_tree, spacy_tree)
        nltk_tree, applied_reduction = self.reduction.apply(nltk_tree, spacy_tree)
        return nltk_tree, (applied_growth + applied_reduction)
