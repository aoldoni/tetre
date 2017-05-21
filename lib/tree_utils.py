from nltk import Tree
from tree import TreeNode, FullSentence


def to_nltk_tree_general(node, attr_list=("dep_", "pos_"), level=99999):
    """Tranforms a Spacy dependency tree into an NLTK tree, with certain spacy tree node attributes serving
    as parts of the NLTK tree node label content for uniqueness.

    Args:
        node: The starting node from the tree in which the transformation will occur.
        attr_list: Which attributes from the Spacy nodes will be included in the NLTK node label.
        level: The maximum depth of the tree.

    Returns:
        A NLTK Tree (nltk.tree)
     """

    # transforms attributes in a node representation
    value_list = [getattr(node, attr) for attr in attr_list]
    node_representation = "/".join(value_list)

    if level == 0:
        return node_representation

    if node.n_lefts + node.n_rights > 0:
        return Tree(node_representation, [to_nltk_tree_general(child, attr_list, level-1) for child in node.children])
    else:
        return node_representation


def to_nltk_tree(node):
    """Creates a fixed representation of a Spacy dependency tree as a NLTK tree. This fixed representation
    will be formed by the Spacy's node attributes: dep_, orth_ and pos_.

    Args:
        node: The starting node from the tree in which the transformation will occur.

    Returns:
        A NLTK Tree (nltk.tree)
     """
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.dep_+"/"+node.orth_+"/"+node.pos_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.dep_+"/"+node.orth_+"/"+node.pos_


def print_tree(sent):
    """Prints a Spacy tree by transforming it in an NLTK tree and using its pretty_print method.
    """
    to_nltk_tree(sent.root).pretty_print()


def group_sorting(groups):
    """Given a group (dictionary) re-orders it as a list in which the group with more elements
    of the "sentences" key is at the beginning of this list.

    Returns:
        A list contaning groups with more sentences at the beginning.
    """
    if isinstance(groups, dict):
        groups = list(groups.values())

    newlist = sorted(groups, key=lambda x: len(x["sentences"]), reverse=True)

    return newlist


def get_node_representation(tetre_format, token):

    params = tetre_format.split(",")

    node_representation = token.pos_
    if token.n_lefts + token.n_rights > 0:
        tree = Tree(node_representation,
                    [to_nltk_tree_general(child, attr_list=params, level=0) for child in token.children])
    else:
        tree = Tree(node_representation, [])

    return tree


def get_token_representation(tetre_format, token):
    string_representation = []
    params = tetre_format.split(",")
    for param in params:
        string_representation.append(getattr(token, param))

    return "/".join(string_representation)


def spacynode_to_treenode(spacy_token, parent = None, root = None, string_representation = ""):
    node = TreeNode(spacy_token.dep_, spacy_token.pos_, spacy_token.orth_,
                    spacy_token.idx, spacy_token.n_lefts, spacy_token.n_rights)

    if isinstance(parent, TreeNode):
        node.set_head(parent)
    elif parent is None:
        node.set_is_root()
    else:
        raise ValueError('Unsupported parent node provided to spacy_to_tree2 method')

    if isinstance(root, TreeNode):
        node.set_root(root)
    elif root is None:
        root = node
        node.set_is_root()
    else:
        raise ValueError('Unsupported root node provided to spacy_to_tree2 method')

    for child in spacy_token.children:
        node.add_child(spacynode_to_treenode(child, node, root))

    return node


def spacysentence_to_fullsentence(spacy_sentence, file_id, sentence_id):
    tree_node   = spacynode_to_treenode(spacy_sentence.root)

    sentence    = FullSentence(tree_node, file_id, sentence_id)
    sentence.set_string_representation(str(spacy_sentence))

    return sentence


def treenode_to_qtree(tree, level = 1, first = True):
    if level < 0:
        return ""

    self_result = " [ "

    if first:
        self_result += " " + tree.to_comparable_value_as_head() + " "
    else:
        self_result += " " + tree.to_comparable_value_as_child() + " "

    if len(tree.children) > 0:
        self_result += " ".join([treenode_to_qtree(node, level-1, False) for node in sorted(tree.children, key=lambda node: node.to_comparable_value_as_child())])

    self_result += " ] "

    return self_result


def nltk_tree_to_qtree(tree):
    self_result = " [ "

    if isinstance(tree, Tree):
        self_result += " " + tree.label() + " "

        if len(tree) > 0:
            self_result += " ".join([nltk_tree_to_qtree(node) for node in sorted(tree)])

    else:
        self_result += " " + str(tree) + " "

    self_result += " ] "

    return self_result


def find_in_spacynode(node, dep, orth):
    
    # print(",".join([node.orth_, orth, node.dep_, dep]))

    if dep != "" and orth != "":
        if dep in node.dep_ and orth == node.orth_:
            return node
    elif orth != "":
        if orth == node.orth_:
            return node
    elif dep != "":
        if dep in node.dep_:
            return node

    if len(node.children) > 0:
        results = []
        for child in node.children:
            results.append(find_in_spacynode(child, dep, orth))
        for result in results:
            if result:
                return result

    return False 


def merge_nodes(nodes, under = False):
    idx = 0
    n_lefts = 0
    n_rights = 0

    for node in nodes:
        idx += node.idx
        n_lefts += node.n_lefts
        n_rights += node.n_rights

    if not under:
        under = TreeNode(nodes[0].dep_, "", "",
                    idx // len(nodes),
                    n_lefts,
                    n_rights)

    for node in nodes:
        under.children.append(node)
        node.head = under

    return under
