from nltk import Tree

def nltk_tree_to_qtree(tree):
    self_result = " [ "

    if (isinstance(tree, Tree)):
        self_result += " " + tree.label() + " "

        if (len(tree) > 0):
            self_result += " ".join([nltk_tree_to_qtree(node) for node in sorted(tree)])

    else:
        self_result += " " + str(tree) + " "

    self_result += " ] "

    return self_result
