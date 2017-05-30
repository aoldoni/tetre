from nltk import Tree


class RuleApplier(object):
    deco_list = []

    def __init__(self):
        """The rule applier class. It provides functionality as to centralize certain structures used into all
        rule applier objects and, more importantly, implements the @RuleApplier.register_function decorator. This
        decorator allows the programmer to, inside a class, mark which methods are rules to be applied directly in the
        tree. These types of rule methods expect a fixed signature and return a fixed set of parameters. An entry point
        then simply applies these rules in the order they were registered. This makes it easier to add/remove rules
        from the ruleset.

        The class with the rules to be applied then extends this RuleApplier class. It can then iterate through the
        rules and apply them by calling the apply method. E.g.: see Process.apply_all()

        """
        # c.f. the grouping at http://universaldependencies.org/u/dep/all.html#al-u-dep/nsubjpass
        # rule1: subject
        self.translation_rules = \
            [
                (['nsubj', 'csubj', 'nsubjpass', 'csubjpass'], 'subj'),
                (['dobj', 'iobj', 'pobj'], 'obj'),
                (['npadvmod', 'amod', 'advmod', 'nummod', 'quantmod', 'rcmod', 'tmod', 'vmod'], 'mod')
            ]
        return

    @staticmethod
    def register_function(func):
        """The static method that serves as the decorator method. It adds a function to the the deco_list static
        list and returns the unaltered function.

        Args:
            func: A method of a class.

        Returns:
            The same method.
        """
        RuleApplier.deco_list.append(func)
        return func

    def get_rules(self):
        """Returns a list with all the rules registered for this class.

        Returns:
             A list with all the rules.
        """

        # Given deco_list is static we need to remove the methods from other classes that are also
        # using this functionality at this point.
        return iter([rule for rule in RuleApplier.deco_list if self.__class__.__name__ in str(rule)])

    def rewrite_dp_tag(self, tag):
        """Given a more complex dependency tag, returns its simplified version according to the rules
        inside self.translation_rules

        Args:
            tag: A string with the more complex dependency tag.

        Returns:
            tag: A string with the simpler dependency tag.
        """
        for rule in self.translation_rules:
            source_tags = rule[0]
            target_tag = rule[1]

            if tag in source_tags:
                return target_tag

        # if no translation rule is found, returns itself
        return tag

    def apply(self, nltk_tree, spacy_tree, tree_root=""):
        """Apply registered rules.

        Args:
            nltk_tree: The tree in the NLTK structure that represents the grouping.
            spacy_tree: The actual TreeNode in which the rules will be extracted from, rooted at the word being
                searched for.
            tree_root: A string containing the dependency tree tag of the immediate child not of the word being
                searched for that will serve as the new root. This new root is used when the rules are applied in the
                child nodes, mostly obj and subj.

        Returns:
            t: The new NLTK tree after rule application.
            applied: A list with the method signatures of the applied rules.
        """

        try:
            root = nltk_tree.label()
        except AttributeError:
            root = str(nltk_tree)

        node_set = []
        if hasattr(nltk_tree, '__iter__'):
            node_set = [node for node in nltk_tree]

        root_spacy_tree = spacy_tree

        if tree_root != "":
            root_spacy_tree = None
            for child in spacy_tree.children:
                if tree_root in child.dep_:
                    root_spacy_tree = child

        applied = []

        if root_spacy_tree is not None:
            for rule in self.get_rules():
                root, node_set, spacy_tree, is_applied = rule(self, root, node_set, root_spacy_tree)

                if is_applied:
                    rule_representation = str(rule).replace("<function ", "")
                    rule_representation = rule_representation[:rule_representation.find(" at")]
                    applied.append(rule_representation)

        t = Tree(root, list(sorted(node_set)))

        return t, applied
