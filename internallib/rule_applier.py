from nltk import Tree

class RuleApplier(object):
    deco_list = []

    def __init__(self):
        self.tags_to_be_removed = set(['punct', 'cc', 'conj', 'mark', ' ', ''])

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
        return iter([rule for rule in RuleApplier.deco_list if self.__class__.__name__ in str(rule)])

    def apply(self, nltk_tree, spacy_tree):

        root = nltk_tree.label()
        node_set = [node for node in nltk_tree]
        
        for rule in self.get_rules():
            root, node_set, spacy_tree = rule(self, root, node_set, spacy_tree)
            # print(self.__class__.__name__, "during", [root, node_set])

        t = Tree(root, list(sorted(node_set)))

        return t