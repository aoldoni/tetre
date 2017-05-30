from tetre.rule_applier import *


class Extraction(RuleApplier):
    def __init__(self):
        """Class with all extraction rules.
        """
        RuleApplier.__init__(self)

    @RuleApplier.register_function
    def raw_subsentences(self, root, node_set, spacy_tree):
        result = {}

        for child in spacy_tree.children:
            if child.no_follow:
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

        return relations


class ProcessExtraction(object):
    def __init__(self):
        """Entry point for the Relation Extraction tool, it loops through all available extraction rules.
        """
        self.extraction = Extraction()

    def apply_all(self, nltk_tree, spacy_tree, sentence):
        """Apply all extraction rules to the provided parameters. This would extract available relations. It is
        expected that at this point that the SpaCy-like tree (TreeNode) was manipulated as to improve the amount
        of rules being extracted. This manipulation is done inside the Growth Reduction Obj and Subj classes.

        Args:
            nltk_tree: The tree in the NLTK structure that represents the grouping.
            spacy_tree: The actual TreeNode in which the rules will be extracted from.
            sentence: The actual raw sentence.

        Returns:
            A list with the applied relations.
        """
        relations = self.extraction.apply(nltk_tree, spacy_tree)
        return relations
