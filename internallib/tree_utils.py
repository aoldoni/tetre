from nltk import Tree
import collections

class TreeNode(object):

    def __init__(self, dep_, pos_, orth_, idx, n_lefts, n_rights):
        self.children = []

        self.dep_ = dep_
        self.pos_ = pos_
        self.orth_ = orth_
        self.idx = idx

        self.n_lefts = n_lefts
        self.n_rights = n_rights

        self.original_string_representation = ""

        self.root = None
        self.head = None
        self.set_is_root()

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, id):
        self.children.pop(id)

    def set_head(self, head):
        self.head = head

    def set_string_representation(self, string_representation):
        self.original_string_representation = string_representation

    def set_is_root(self):
        self.head = self
        self.root = self

    def is_root(self):
        return self.head == self

    def set_root(self, root):
        self.root = root

    def to_sentence_list(self):
        sorted_sentence = sorted(list(flatten_list(self.to_sentence_list_internal())), key=lambda obj: obj.idx)
        return sorted_sentence

    def to_sentence_string(self):
        return " ".join([t.orth_ for t in self.to_sentence_list()])

    def to_sentence_list_internal(self):
        sentence = [self] + [child.to_sentence_list_internal() for child in self.children]
        return sentence

    def to_tree_string(self):
        "\n" + self.orth_ + "/" + self.dep_ + "/" + self.pos_ + " [ ".join([str(child) for child in self.children]) + " ] "

    def __str__(self):
        if (len(self.original_string_representation) > 0):
            return self.original_string_representation
        else:
            return self.orth_

    # def __iter__(self):
    #     return self

    # def __next__(self):
    #     try:
    #         result = self.text[self.index].upper()
    #     except IndexError:
    #         raise StopIteration
        
    #     self.index += 1
    #     return result

def spacy_to_treenode(spacy, parent = None, root = None, string_representation = ""):
    node = TreeNode(spacy.dep_, spacy.pos_, spacy.orth_, \
                    spacy.idx, spacy.n_lefts, spacy.n_rights)

    if isinstance(parent, TreeNode):
        node.set_head(parent)
    elif parent is None:
        node.set_string_representation(string_representation)
        node.set_is_root()
    else:
        raise ValueError('Unsupported parent node provided to spacy_to_tree2 method')

    if isinstance(root, TreeNode):
        node.set_root(root)
    elif root is None:
        root = node
    else:
        raise ValueError('Unsupported root node provided to spacy_to_tree2 method')

    for child in spacy.children:
        node.add_child(spacy_to_treenode(child, node, root))

    return node

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

def flatten_list(l):
    for el in l:
        if isinstance(el, list) and not isinstance(el, (str, bytes)):
            yield from flatten_list(el)
        else:
            yield el