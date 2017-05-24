from graphviz import Digraph

from parsers_cache import get_cached_sentence_image
from directories import dirs
from tree_utils import nltk_tree_to_qtree


class GroupImageNameGenerator(object):
    file_extension = "png"
    base_image_path = "images/"

    def __init__(self, base, word, file_id=""):
        """This class is responsible for generating the names of the images, given the context.

        Args:
            base: The root of the file name.
            word: The word being currently searched.
            file_id: The ID of this current file being generated.
        """
        self.base = base
        self.word = word
        self.file_id = file_id

    def get_base_path(self):
        """Concatenates the pieces to form the file path.

        Returns:
            A string with the image name, without an extension.
        """
        return self.base + "-" + self.word + "-" + self.file_id

    def get_base_path_with_extension(self):
        """Concatenates the pieces to form the file path.

        Returns:
            A string with the image path + name, with an extension.
        """
        return self.base_image_path + self.get_base_path() + "." + self.file_extension

    def get_render_path(self):
        """Concatenates the pieces to form the file path.

        Returns:
            A string with the full path to the image, without an extension.
        """
        return dirs['output_html']['path'] + self.base_image_path + self.get_base_path()


class ResultsGroupMatcher(object):
    def __init__(self, argv):
        """This class is responsible for matching sentences into groups of sentences.

        Args:
            argv: The command line arguments.
        """
        self.argv = argv
        self.groups = {}
        self.current_group_id = 0

    def get_groups(self):
        """A getter for the internal groups data structure.

        Returns:
            A dictionaty with the groups of sentences.
        """
        return self.groups

    def set_groups(self, groups):
        """A setter for the internal groups data structure.

        Args:
            groups: A dictionaty with the groups of sentences.
        """
        self.groups = groups

    def group_accounting_add(self, tree, token, sentence, img_path, representative,
                             img_renderer, extracted_relations=(), applied=()):
        """Adds a new sentence to its correct group.

        Args:
            tree: The NLTK tree with the node representation.
            token: The TreeNode SpaCy-like node.
            sentence: The raw sentence text.
            img_path: The path to the image related to this sentence.
            representative: The NLTK tree or TreeNode SpaCy-like node that represents this group.
            img_renderer: The GroupImageRenderer object related to this command.
            extracted_relations: The relations extracted.
            applied: The applied rules that helped with the relations extraction.
        """

        # generates the key for this sentences group
        group_key = nltk_tree_to_qtree(tree)

        if group_key in self.groups:
            group = self.groups[group_key]

            group["sentences"].append({
                "sentence": sentence,
                "token": token,
                "img_path": img_path,
                "rules": extracted_relations,
                "applied": applied
            })

        else:
            img = ""

            if self.argv.tetre_output == "html":
                img = img_renderer.gen_group_image(representative)

            self.groups[group_key] = {"representative": tree,
                                      "params": len(tree),
                                      "img": img,
                                      "sentences": [
                                          {"sentence": sentence,
                                           "token": token,
                                           "img_path": img_path,
                                           "rules": extracted_relations,
                                           "applied": applied}
                                          ]}

    def get_max_params(self):
        """Returns the maximum number of parameters in a tree.

        Returns:
            integer
        """
        max_params = 0

        for group in self.groups.values():
            if group["params"] > max_params:
                max_params = group["params"]

        return max_params

    def get_average_per_group(self):
        """Returns the average number sentences in a group.

        Returns:
            integer
        """
        return int(self.get_sentence_totals() / len(self.groups))

    def get_sentence_totals(self):
        """Returns the total numbers of sentences.

        Returns:
            integer
        """
        total = 0

        for key, group in self.groups.items():
            total += len(group["sentences"])

        return total


class SentencesAccumulator(object):
    base_image_name = 'sentence'

    def __init__(self, argv):
        """This class is responsible for accumulating the sentences being processed and generate their images.

        Args:
            argv: The arguments from the command line.
        """
        self.argv = argv
        self.sentence_imgs = []
        self.sentence = []
        self.current_token_id = 0
        self.current_sentence_id = 0

    def process_sentence(self, sentence):
        """Accumulating the sentences being processed and generate their images.

        Args:
            sentence: The string sentence raw text.

        Returns:
            A string with the image directory in case the output of the HTML format. Otherwise it returns an empty
            string.
        """
        self.sentence.append(str(sentence).replace("\r", "").replace("\n", "").strip())
        if self.argv.tetre_output == "html":
            return self.sentence_to_graph(sentence)
        else:
            return ""

    def sentence_to_graph(self, sentence):
        """Generates sentence dependency tree image.

        Args:
            sentence: The string sentence raw text.

        Returns:
            A string with the image directory.
        """
        name_generator = GroupImageNameGenerator(self.base_image_name,
                                                 self.argv.tetre_word,
                                                 str(sentence.file_id) + "-" + str(sentence.id))

        self.sentence_imgs.append(name_generator.get_base_path_with_extension())

        found = get_cached_sentence_image(self.argv,
                                          dirs['output_html']['path'],
                                          name_generator.get_base_path_with_extension())

        if not found:
            e = Digraph(self.argv.tetre_word, format=GroupImageNameGenerator.file_extension)
            e.attr('node', shape='box')
            e.attr('graph', label=str(sentence))

            current_id = self.current_token_id
            self.sentence_to_graph_add_node(e, current_id, sentence.root.orth_)
            self.sentence_to_graph_recursive(sentence.root, current_id, e)
            e.render(name_generator.get_render_path())

        self.current_sentence_id += 1

        return name_generator.get_base_path_with_extension()

    def sentence_to_graph_recursive(self, token, parent_id, e):
        """Recursive function on each node as to generates the sentence dependency tree image.

        Args:
            token: The string token raw text.
            parent_id: The id of the parent node this token is a child of in the dependency tree.
            e: The graphical object (graphviz.Digraph).
        """
        if len(list(token.children)) == 0:
            return

        current_global_id = {}

        for child in token.children:
            self.current_token_id += 1
            current_global_id[str(self.current_token_id)] = child

        for child_id, child in current_global_id.items():
            self.sentence_to_graph_add_node(e, child_id, child.orth_)
            e.edge(str(parent_id), child_id, label=child.dep_)

        for child_id, child in current_global_id.items():
            self.sentence_to_graph_recursive(child, child_id, e)

    def sentence_to_graph_add_node(self, e, current_id, orth_):
        """Adds node to the image being prepared.

        Args:
            e: The graphical object (graphviz.Digraph).
            current_id: The id of the parent node this token is a child of in the dependency tree.
            orth_: The string token raw text.
        """
        if orth_ == self.argv.tetre_word:
            e.node(str(current_id), orth_, fillcolor="dimgrey", fontcolor="white", style="filled")
        else:
            e.node(str(current_id), orth_)
