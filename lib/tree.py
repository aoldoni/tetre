

class TreeNode(object):
    def __init__(self, dep_, pos_, orth_, idx, n_lefts, n_rights):
        """Constructs a TreeNode. A TreeNode is a mirror object of a SpaCy token (spacy.token) however intended
        to be Pickable for caching purposes. This allows iterations where new rules for information extraction
        to be tested much faster given iterations between runs are faster and raw text does not need to be
        re-parsed every time.

        Args:
            dep_: The dependency tag.
            pos_: The part of speech tag.
            orth_: The orthography (the token itself).
            idx: A global id for this token.
            n_lefts: Number of child nodes to the left.
            n_rights: Number of child nodes to the right.
        """

        self.children = []

        self.comparing_rule_head = ["pos_"]
        self.comparing_rule_child = ["dep_"]

        self.dep_ = dep_
        self.pos_ = pos_
        self.orth_ = orth_
        self.idx = idx

        self.n_lefts = n_lefts
        self.n_rights = n_rights

        self.no_follow = False

        self.root = None
        self.head = None
        self.set_is_root()

    def add_child(self, child):
        """Adds a child node to an existing node.

        Args:
            child: The new child.
        """
        self.children.append(child)

    def remove_child(self, node_id):
        """Given a list poisition, removed the child from the list of children.

        Args:
            node_id: The id to be removed from the list.
        """
        self.children.pop(node_id)

    def set_head(self, head):
        """Sets the new head/parent for this TreeNode node.

        Args:
            head: The new node whch is the head/parent of the current node.
        """
        self.head = head

    def set_is_root(self):
        """Modified data structure as to define that this node is the root node of the entire tree.
        """
        self.head = self
        self.root = self

    def is_root(self):
        """Checks if this node is the tree root.

        Returns:
            A boolean, True if this node is the root, False otherwise.
        """
        return self.head == self

    def set_root(self, root):
        """Sets the new node as the root for this TreeNode node.

        Args:
            root: The node that is the root.
        """
        self.root = root

    @staticmethod
    def sort(flat_list):
        """Sort a flattened version of the list, based on the sentence position (idx attribute).

        Args:
            flat_list: The list of nodes to be sorted.
        """
        return sorted(list(flat_list), key=lambda obj: obj.idx)

    def to_sentence_list(self, to_sort=True):
        """Returns a flat list of the nodes of this tree. It can be sorted as per their original position in
        the sentence.

        Args:
            to_sort: A Boolean parameter, specifying if the list should be sorted (as per their original position in
                the sentence).

        Returns:
            The list of nodes.
        """
        if to_sort:
            sorted_sentence = self.sort(flatten_list(self.to_sentence_list_internal()))
        else:
            sorted_sentence = flatten_list(self.to_sentence_list_internal())

        return sorted_sentence

    def to_sentence_string(self):
        """Returns a string with a reconstructed version of the original sentence this tree represents.

        Returns:
            A string constaining a reconstructed version of the original sentence.
        """
        return " ".join([t.orth_ for t in self.to_sentence_list()])

    def to_sentence_list_internal(self):
        """Transforms this tree in a list. Ignores branches marked through the "no_follow" attribute.

        Returns:
            A list containig each node of the tree.
        """
        if self.no_follow:
            return []

        sentence = [self] + [child.to_sentence_list_internal() for child in self.children if not child.no_follow]
        return sentence

    def to_tree_string(self, level=1):
        """Returns a string representation of the tree for debugging purposes.

        Args:
            level: The current level of the tree, used for spacing. Should not be passed by the caller.

        Returns:
            A string constaining a representation of this tree.
        """
        self_representation = "\n" + (level*"\t") + "  (" + self.orth_ + "/" + self.dep_ + "/" + self.pos_ + ")  "

        if len(self.children) > 0:
            return self_representation + " [ " +\
                   "".join([child.to_tree_string(level+1) for child in self.children]) + " ] "

        return self_representation

    def to_comparable_value_as_child(self):
        """Returns a comparable version of this node.

        Returns:
            A string constaining a representation of this node.
        """
        result = []
        for rule in self.comparing_rule_child:
            result.append(getattr(self, rule))

        return "/".join(result)

    def to_comparable_value_as_head(self):
        """Returns a comparable version of this node.

        Returns:
            A string constaining a representation of this node.
        """
        result = []
        for rule in self.comparing_rule_head:
            result.append(getattr(self, rule))

        return "/".join(result)

    def __str__(self):
        """Returns the string version of this node.

        Returns:
            A string constaining a representation of this node.
        """
        return self.orth_


class FullSentence(object):
    def __init__(self, root, file_id, sentence_id):
        """Constructs a FullSentence. A FullSentence is a wrapper around a TreeNode that is also Pickable and contains
        some metadata.

        Args:
            root: The node which is the root of the sentence in the dependency tree (TreeNode).
            file_id: A number identifyng the file being processed. It is expected to be stable
                (e.g.: same file always receives same id).
            sentence_id: A number identifyng the sentence being processed. It is expected to be stable
                (e.g.: same sentence always receives same id).
        """

        self.iterable = []
        self.root = root
        self.string_representation = ""
        self.pointer = 0
        self.file_id = file_id
        self.id = sentence_id

    def set_string_representation(self, string_representation):
        """Sets the original raw string before it was parsed to form this sentence. The SpaCy segmenter is used
        to determine the strings.

        Args:
            string_representation: The original string representation of this sentence.
        """
        self.string_representation = string_representation

    def __iter__(self):
        """Prepares the list (self.iterable) containing the nodes of the tree to be iterated upon.

        Returns:
            The FullSentence object itself.
        """
        self.pointer = 0
        self.iterable = self.root.to_sentence_list()
        return self

    # Declared in Python3 style
    def __next__(self):
        """Returns the current node of the iteration.

         Returns:
             The TreeNode object being referenced in the list.
         """
        if self.pointer >= len(self.iterable):
            raise StopIteration

        next_value = self.iterable[self.pointer]
        self.pointer += 1

        return next_value

    # Python2 compatibility
    next = __next__

    def __str__(self):
        """Returns the original string representation of this sentence

         Returns:
             A string with the sentence.
         """
        return self.string_representation


def flatten_list(l):
    """Given a list of lists, yields a flattened version of this list.

     Yields:
         A list.
     """
    for el in l:
        if isinstance(el, list) and not isinstance(el, (str, bytes)):
            # python3 version converted back to python2 version:
            # yield from flatten_list(el)
            for sublist in flatten_list(el):
                yield sublist
        else:
            yield el
