from nltk import Tree
import collections


class TreeNode(object):

    def __init__(self, dep_, pos_, orth_, idx, n_lefts, n_rights):
        self.children = []

        self.comparing_rule_head    = ["pos_"]
        self.comparing_rule_child   = ["dep_"]

        self.dep_ = dep_
        self.pos_ = pos_
        self.orth_ = orth_
        self.idx = idx

        self.n_lefts = n_lefts
        self.n_rights = n_rights

        self.nofollow = False

        self.root = None
        self.head = None
        self.set_is_root()

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, id):
        self.children.pop(id)

    def set_head(self, head):
        self.head = head

    def set_is_root(self):
        self.head = self
        self.root = self

    def is_root(self):
        return self.head == self

    def set_root(self, root):
        self.root = root

    def sort(self, flat_list):
        return sorted(list(flat_list), key=lambda obj: obj.idx)

    def to_sentence_list(self, to_sort=True):
        if (to_sort):
            sorted_sentence = self.sort(flatten_list(self.to_sentence_list_internal()))
        else:
            sorted_sentence = flatten_list(self.to_sentence_list_internal())

        return sorted_sentence

    def to_sentence_string(self):
        return " ".join([t.orth_ for t in self.to_sentence_list()])

    def to_sentence_list_internal(self):
        if self.nofollow == True:
            return []

        sentence = [self] + [child.to_sentence_list_internal() for child in self.children if not child.nofollow]
        return sentence

    def to_tree_string(self, level = 1):
        self_representation = "\n" + (level*"\t") + "  (" + self.orth_ + "/" + self.dep_ + "/" + self.pos_ + ")  "

        if len(self.children) > 0:
            return self_representation + " [ " + "".join([child.to_tree_string(level+1) for child in self.children]) + " ] "

        return self_representation

    def to_comparable_value_as_child(self):
        result = []
        for rule in self.comparing_rule_child:
            result.append(getattr(self,rule))

        return "/".join(result)

    def to_comparable_value_as_head(self):
        result = []
        for rule in self.comparing_rule_head:
            result.append(getattr(self,rule))

        return "/".join(result)

    def __str__(self):
        return self.orth_

    # def __eq__(self, other): 
    #     if self.__class__ is not other.__class__:
    #         return False

    #     for rule in self.comparing_rule_head:
    #         if not getattr(self,rule) == getattr(self,other):
    #             return False

    #     # Parents are the same, continue checking the children.
    #     return recursive_child_compare(self, other)

    # @staticmethod    
    # def recursive_child_compare(self, other):
    #     other_list = list(other.children)

    #     for child in self.children:
    #         if child in other_list:

    #     # This code is incomplete
    #     for rule in self.comparing_rule_head:
    #         if not getattr(self,rule) == getattr(self,other):
    #             return False


class FullSentence(object):
    def __init__(self, root, file_id, sentence_id):
        self.iterable = []
        self.root = root
        self.string_representation = ""
        self.pointer = 0
        self.file_id = file_id
        self.id = sentence_id

    def set_string_representation(self, string_representation):
        self.string_representation = string_representation

    def __iter__(self):
        self.pointer = 0
        self.iterable = self.root.to_sentence_list()
        return self

    def __next__(self):
        if self.pointer >= len(self.iterable):
            raise StopIteration

        next_value = self.iterable[self.pointer]
        self.pointer += 1

        return next_value

    def __str__(self):
        return self.string_representation


def spacynode_to_treenode(spacy_token, parent = None, root = None, string_representation = ""):
    node = TreeNode(spacy_token.dep_, spacy_token.pos_, spacy_token.orth_, \
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

    if (len(tree.children) > 0):
        self_result += " ".join([treenode_to_qtree(node, level-1, False) for node in sorted(tree.children, key=lambda node: node.to_comparable_value_as_child())])

    self_result += " ] "

    return self_result


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

def find_in_spacynode(node, dep, orth):
    if dep in node.dep_ and orth == node.orth_:
        return node

    if len(node.children) > 0:
        results = []
        for child in node.children:
            results.append(find_in_spacynode(child, dep, orth))
        for result in results:
            if result != False:
                return result

    return False 