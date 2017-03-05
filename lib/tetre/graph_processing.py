from nltk import Tree
from types import FunctionType
from lib.dependency_helpers import *
from lib.rule_applier import *
from lib.tree_utils import find_in_spacynode, merge_nodes
import inspect
from functools import wraps, reduce
import sys

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
            "2 Related work Learning to rank has been a promising research area which continuously improves web search relevance (Burges et al."

            The dependency parser puts not the action the improves something as a parent of the word "improves" in the in the tree, and adds to it the relcl relation.
            This method adjusts the tree, bringing the node above under "improves".


            2) Consider the following sentence:
            "The best known recovery algorithm for dirty mapping entries, proposed in LazyFTL, exhibits two shortcomings that GeckoFTL improves upon."

            In this case, GeckoFTL is is a proper noun, so it shouldn't be replaced.
        """

        isApplied = False

        upwards = ["relcl", "ccomp"]

        #adjust tree
        token = spacy_tree
        token_head = spacy_tree

        # print("0", token.to_tree_string())
        # print("0", token_head.to_tree_string())

        if (token_head.dep_ in upwards and token_head.head != token):
            token_head = token_head.head

            # print("1", token.to_tree_string())
            # print("1", token_head.to_tree_string())

            isChangingPossibilities = []
            isChanging = False
            hasSubj = False

            children_list = token.children[:]
            for i in range(0, len(children_list)):
                if (children_list[i].dep_ in self.subs):
                    hasSubj = True

                    # print(token.children[i].orth_, token.children[i].pos_)
                    
                    if not (token.children[i].pos_ in ["NOUN", "PROPN", "VERB", "NUM", "PRON", "X"]):
                        token.children.pop(i)
                        isChangingPossibilities.append(True)
                    else:
                        isChangingPossibilities.append(False)

                    # print(isChanging)
                    # print()

            if True in isChangingPossibilities:
                isChanging = True

            if not hasSubj:
                isChanging = True

            # print(isChanging)
            # print()

            # print("2", hasSubj)
            # print("2", isChanging)
            # print("2", token.to_tree_string())
            # print("2", token_head.to_tree_string())

            if (isChanging):
                isApplied = True
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

        return root, node_set, spacy_tree, isApplied

    @RuleApplier.register_function
    def recurse_on_dep_conj_if_no_subj(self, root, node_set, spacy_tree):
        """
            1) Consider the following sentence:
            "Using many ASR hypotheses helps recover the ASR errors of NE words in 1-best ASR results and improves NER accuracy."

            The dependency parser puts not the action the improves something as a parent of the word "improves" in the in the tree, and adds to it the conj relation.
            This method adjusts the tree, bringing the node above under "improves".

            
            2) Now consider the following sentence:
            "Both identify product features from reviews, but OPINE significantly improves on both."

            Note how, although improves is a conj, "Both" is the subj up the tree. However, there is a "but" as the "cc", and beucase of this we need to pick the "conj" below instead of the "subj".

            3) Now consider:
            "SFS [6] (sort-filter-skyline) is based on the same rationale as BNL , but improves performance by first sorting the data according to a monotone function."

            This has a "but", however no other conj, in this case we should use the nsubj again.

            4) Now consider:
            "[16] studies the usage of grammars and LZ77 parsing for compression of similar sequence collections and improves complexity bounds with respect to space as well as time."

            The subj is actually the dobj of the head
        """

        isApplied = False

        upwards = ["conj"]

        token = spacy_tree
        token_head = spacy_tree

        while True:

            if (token_head.dep_ in upwards        \
                and token_head.head != token_head \
                and len([child for child in token.children if child.dep_ in self.subs]) == 0):

                # print("pre1", token_head)
                
                token_head = token_head.head

                # print("pre2", token_head)

                # needs_loop = True
                # while needs_loop:

                changed = False
                children_list = token_head.children[:]

                isBut           = False
                otherConjExists = False
                hasSubj         = False
                hasObj          = False

                for j in range(0, len(children_list)):
                    if token_head.children[j].dep_ in "cc" \
                        and token_head.children[j].orth_ == "but":
                        isBut = True
                    if token_head.children[j].dep_ in "conj" \
                        and token_head.children[j] != token:
                        otherConjExists = True
                    if "subj" in token_head.children[j].dep_:
                        hasSubj = True
                    if "obj" in token_head.children[j].dep_:
                        hasObj = True

                for i in range(0, len(children_list)):

                    # print()
                    # print("0", isBut)
                    # print("0", token_head.children[i].dep_)
                    # print("0", token_head.children[i].orth_)
                    # print("0", token.orth_)

                    isOtherConj = token_head.children[i].dep_ == "conj" and token_head.children[i] != token
                    isSubj = token_head.children[i].dep_ in self.subs
                    isObj = token_head.children[i].dep_ in self.objs

                    nodeResult = find_in_spacynode(token_head.children[i], token.dep_, token.orth_)
                    if nodeResult != False:
                        isSubChild = True
                    else:
                        isSubChild = False

                    cond_subj = not isBut and isSubj
                    cond_dobj = not isBut and not hasSubj and isObj
                    cond_conj_other = isBut and not isSubj and otherConjExists and isOtherConj and not isSubChild
                    cond_conj_same  = isBut and not otherConjExists and isSubj

                    # print("1", isOtherConj)
                    # print("1", cond_subj)
                    # print("1", cond_conj_other)
                    # print("1", cond_conj_same)
                    # print("1", isBut)

                    if  (cond_subj) or \
                        (cond_conj_other) or \
                        (cond_dobj) or \
                        (cond_conj_same):

                        isApplied = True

                        # print("2", token.to_tree_string())
                        # print("2", token_head.to_tree_string())
                        # print("2", token_head.children[i].to_tree_string())
                        # print("2", node_set)
                        # print("2", isBut)

                        if cond_dobj or cond_conj_other:
                            token_head.children[i].dep_ = self.downwards_subj

                        # adjust representation
                        node_set.append(token_head.children[i].dep_ )

                        #adjust actual tree
                        token.children.append(token_head.children[i])
                        token_head.children[i].head = token
                        token_head.children.pop(i)

                        # print("3", token.to_tree_string())
                        # print("3", token_head.to_tree_string())
                        # print("3", node_set)
                        # print("3", isBut)

                        # print("---------------------------------------------------------------------")
                        # print()

                        changed = True
                        break

                    # if not changed:
                    #     needs_loop = False

            else:
                break

        return root, node_set, spacy_tree, isApplied

    @RuleApplier.register_function
    def transform_xcomp_to_dobj_or_sub_if_doesnt_exists(self, root, node_set, spacy_tree):
        """
            1) Consider the sentence:
            xcomp > "Recent work has showed that structured retrieval improves answer ranking for factoid questions: Bilotti et al."
            ccomp > "The Fat-Btree structure presented in [19] vastly reduces the index-modification cost and improves the dynamic data skew handling method."

            Although it is possible to understand that "structured retrieval" "improves" "answer ranking..." the "answer ranking..." part is
            not presented as a dobj dependency, but a xcomp dependency instead. This rule transforms xcomp into "obj" as both contain the same
            purpose for information extraction.

            2) Consider this sentence:
            ccomp > "2 Related Work Caching frequently accessed data at the client side not only improves the userÃ¢Â€Â™s experience of the distributed system, but also alleviates the serverÃ¢Â€Â™s workload and enhances its scalability."

            Although in this sentence the dobj was detected, the ccomp is the nsubj. Thus, after replacing the items for dobj, if there is no nsubj in the sentence we try to tranform then in nsubj.
        """

        isApplied = False

        should_return = False

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
                    isApplied = True

                    child.dep_ = target
                    node_set = [target if node==replace else node for node in node_set]
                    break

        node_set = set([self.rewrite_dp_tag(node) for node in node_set])
        return root, node_set, spacy_tree, isApplied

    @RuleApplier.register_function
    def transform_prep_in_to_dobj(self, root, node_set, spacy_tree):
        """
            1) Consider the following sentence:
            "While matrix factorization is widely used in recommender systems, matrix co-factorization helps to handle multiple aspects of the data and improves in predicting individual decisions (Hong et al. "

            One can see that "matrix co-factorization" and improves "predicting individual decisions". It could be rewriting as "improves prediction of individual decisions". Thus anything after a "prep in" could be considered an "obj".
        """
        isApplied = False

        target = "obj"
        replace = "prep"

        is_obj = False
        for child in spacy_tree.children:
            if target in child.dep_:
                is_obj = True

        for child in spacy_tree.children:
            if replace in child.dep_ and child.orth_ == "in":
                if not is_obj:
                    isApplied = True

                    child.dep_ = target
                    node_set = [target if node==replace else node for node in node_set]

        node_set = list(set([self.rewrite_dp_tag(node) for node in node_set]))
        return root, node_set, spacy_tree, isApplied

    @RuleApplier.register_function
    def add_dobj_if_dep_is_subj(self, root, node_set, spacy_tree):
        """
            1) Consider the following sentence:
            "Turney (2005) extends the above approach by introducing the latent relational analysis (LRA), which uses automatically generated synonyms, learns suitable patterns, and performs singular value decomposition in order to smooth the frequencies."
            "This work uses materialized views to further benefit from commonalities across queries."

            In the first sentence, the relation uses(which; automatically generated synonyms) could have been extracted by getting the nsubj dependency and transforming it to be the child's dobj. The same is valid for the second example.
        """
        isApplied       = False

        token = spacy_tree
        token_head = token.head

        hasSubj         = False
        hasObj          = False

        for j in range(0, len(token.children)):
            if "subj" in token.children[j].dep_:
                hasSubj = True
            if "obj" in token.children[j].dep_:
                hasObj = True

        # print(0, hasObj, hasSubj, "subj" in token.dep_ and hasSubj and not hasObj)

        if ("subj" in token.dep_ and hasSubj and not hasObj):
            isApplied = True
            
            children_list = token_head.children[:]

            for i in range(0, len(children_list)):
                if (children_list[i].idx == token.idx):
                    token_head.children.pop(i)

                    #adjust representation
                    node_set.append(self.downwards_obj)

            token_head.dep_ = self.downwards_obj
            token.children.append(token_head)
            token_head.head = token

        return root, node_set, spacy_tree, isApplied


class Reduction(RuleApplier):
    def __init__(self):
        RuleApplier.__init__(self)
        self.tags_to_be_removed = set(['punct', 'mark', ' ', '', 'meta'])

    @RuleApplier.register_function
    def remove_duplicates(self, root, node_set, spacy_tree):
        """
            1) This groups sentence with e.g.: multiple "punct" into the same group for easier analysis.
        """
        return root, set(node_set), spacy_tree, False

    @RuleApplier.register_function
    def remove_tags(self, root, node_set, spacy_tree):
        """
            1) This removes dependency paths of the types contained in self.tags_to_be_removed as they are not considered
            relevant. This reduces the number of different groups.
        """
        isApplied = False

        node_set = set(node_set) - self.tags_to_be_removed

        for child in spacy_tree.children:
            if child.dep_ in self.tags_to_be_removed:
                isApplied = True
                child.nofollow = True

        return root, node_set, spacy_tree, isApplied

    @RuleApplier.register_function
    def transform_tags(self, root, node_set, spacy_tree):
        """
            1) This transform tags from several variations into a more general version. The mappings are contained
            in the self.translation_rules variables.
        """
        node_set = set([self.rewrite_dp_tag(node) for node in node_set])
        return root, node_set, spacy_tree, False

    @RuleApplier.register_function
    def merge_multiple_subj_or_dobj(self, root, node_set, spacy_tree):
        """
            1) Unify multiple subj and fix representation:
            "Another partitional method ORCLUS [2] improves PROCLUS by selecting principal components so that clusters not parallel to the original dimensions can also be detected."

            It has 2 nsubj: "Another partitional method" and "ORCLUS [2]". They should be in the same sentence.
            Because it has 2 subj, the representation ends up being the one from the last nsubj.
        """

        # return root, node_set, spacy_tree, False

        isApplied = False

        groups = ["subj", "obj"]
        
        for group in groups:
            this_group = []

            count = reduce(lambda x, y: x + 1 if group in y.dep_ else x, spacy_tree.children, 0)

            # print("group", group, count)

            if count < 2:
                continue;

            changed = True
            while changed:
                changed = False
                children_list = spacy_tree.children[:]

                for i in range(0, len(children_list)):
                    if group in children_list[i].dep_:
                        this_group.append(children_list[i])
                        spacy_tree.children.pop(i)

                        # print("group", group, count)

                        isApplied = True
                        changed = True
                        break

            child = merge_nodes(this_group)
            spacy_tree.children.append(child)
            child.head = spacy_tree

        return root, node_set, spacy_tree, isApplied

class Process(object):
    def __init__(self):
        self.growth = Growth()
        self.reduction = Reduction()
        return

    def applyAll(self, nltk_tree, spacy_tree):

        # print("will process")

        nltk_tree, applied_growth = self.growth.apply(nltk_tree, spacy_tree)
        nltk_tree, applied_reduction = self.reduction.apply(nltk_tree, spacy_tree)
        return nltk_tree, (applied_growth + applied_reduction)
