from nltk import Tree

class RuleApplier(object):
    deco_list = []

    def __init__(self):
        ## c.f. the grouping at http://universaldependencies.org/u/dep/all.html#al-u-dep/nsubjpass
        ##
        # rule1: subject
        self.translation_rules = \
        [
            (['nsubj', 'csubj', 'nsubjpass', 'csubjpass'], 'subj'),
            (['dobj','iobj','pobj'], 'obj'),
            (['npadvmod', 'amod', 'advmod', 'nummod', 'quantmod', 'rcmod', 'tmod', 'vmod'], 'mod')
        ]
        return

    @staticmethod
    def register_function(func):
        RuleApplier.deco_list.append(func)
        return func

    def get_rules(self):
        # print("----------------------------------")
        # print(self.__class__.__name__)
        # print(RuleApplier.deco_list)
        # print("----------------------------------")
        return iter([rule for rule in RuleApplier.deco_list if self.__class__.__name__ in str(rule)])

    def rewrite_dp_tag(self, tag):
        for rule in self.translation_rules:
            source_tags = rule[0]
            target_tag = rule[1]

            if tag in source_tags:
                return target_tag

        # if nothing, return itself
        return tag

    def apply(self, nltk_tree, spacy_tree, tree_root = ""):

        try:
            root = nltk_tree.label()
        except AttributeError:
            root = str(nltk_tree)

        node_set = []
        if hasattr(nltk_tree, '__iter__'):
            node_set = [node for node in nltk_tree]

        root_spacy_tree = spacy_tree

        # print("1 root", tree_root, root, node_set, root_spacy_tree, spacy_tree)

        if tree_root != "":
            root_spacy_tree = None
            for child in spacy_tree.children:
                if tree_root in child.dep_:
                    root_spacy_tree = child

        # print("2 root", tree_root, root, node_set, root_spacy_tree, spacy_tree)

        applied = []

        if root_spacy_tree != None:
            for rule in self.get_rules():
                # print(self.__class__.__name__, rule, "during", [root, node_set])
                root, node_set, spacy_tree, is_applied = rule(self, root, node_set, root_spacy_tree)

                if is_applied:
                    rule_representation = str(rule).replace("<function ","")
                    rule_representation = rule_representation[:rule_representation.find(" at")]
                    applied.append(rule_representation)

        t = Tree(root, list(sorted(node_set)))

        return t, applied