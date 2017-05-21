

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

    @staticmethod
    def sort(flat_list):
        return sorted(list(flat_list), key=lambda obj: obj.idx)

    def to_sentence_list(self, to_sort=True):
        if to_sort:
            sorted_sentence = self.sort(flatten_list(self.to_sentence_list_internal()))
        else:
            sorted_sentence = flatten_list(self.to_sentence_list_internal())

        return sorted_sentence

    def to_sentence_string(self):
        return " ".join([t.orth_ for t in self.to_sentence_list()])

    def to_sentence_list_internal(self):
        if self.nofollow:
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

    # Declared in Python3 style
    def __next__(self):
        if self.pointer >= len(self.iterable):
            raise StopIteration

        next_value = self.iterable[self.pointer]
        self.pointer += 1

        return next_value

    # Python2 compatibility
    next = __next__

    def __str__(self):
        return self.string_representation


def flatten_list(l):
    for el in l:
        if isinstance(el, list) and not isinstance(el, (str, bytes)):
            # python3 version converted back to python2 version:
            # yield from flatten_list(el)
            for sublist in flatten_list(el):
                yield sublist
        else:
            yield el