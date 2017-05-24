from graphviz import Digraph

from django.utils.safestring import mark_safe
from django.template import Template, Context

from tetre.command_utils import setup_django_template_system
from tetre.command import SentencesAccumulator, ResultsGroupMatcher, GroupImageNameGenerator

from directories import dirs
from parsers import get_tokens, highlight_word
from tree_utils import to_nltk_tree_general, group_sorting, get_node_representation


class GroupImageRenderer(object):
    base_image_name = 'command-group'

    def __init__(self, argv):
        """Generates the images for each group of sentences.

        Args:
            argv: The command line arguments.
        """
        self.argv = argv
        self.current_token_id = 0
        self.current_group_id = 0

        self.take_pos_into_consideration = len(
            [params for params in self.argv.tetre_format.split(",") if params == "pos_"])

    def gen_group_image(self, token, depth=1):
        """Generates the images based on the node that represents this group.

        Args:
            token: The Treenode node.
            depth: integer 1 by default, as we are only interested in the first level.

        Returns:
            A string with the image path.
        """
        e = Digraph(self.argv.tetre_word, format=GroupImageNameGenerator.file_extension)
        e.attr('node', shape='box')

        current_id = self.current_token_id
        e.node(str(current_id), token.pos_)

        self.group_to_graph_recursive_with_depth(token, current_id, e, depth)

        name_generator = GroupImageNameGenerator(self.base_image_name, self.argv.tetre_word, str(self.current_group_id))
        e.render(name_generator.get_render_path())

        self.current_group_id += 1

        return name_generator.get_base_path_with_extension()

    def group_to_graph_recursive_with_depth(self, token, parent_id, e, depth):
        """Generates the images based on the node that represents this group (internal call for depths-1).

        Args:
            token: The Treenode node.
            parent_id: The id of the parent node this token is a child of in the dependency tree.
            e: The graphical object (graphviz.Digraph).
            depth: integer 1 by default, as we are only interested in the first level.
        """
        if len(list(token.children)) == 0 or depth == 0:
            return

        current_global_id = {}

        for child in token.children:
            self.current_token_id += 1
            current_global_id[str(self.current_token_id)] = child

        for child_id, child in current_global_id.items():
            if self.take_pos_into_consideration:
                e.node(child_id, child.pos_)
            else:
                e.node(child_id, "???")
            e.edge(str(parent_id), child_id, label=child.dep_)

        for child_id, child in current_global_id.items():
            self.group_to_graph_recursive_with_depth(child, child_id, e, depth - 1)


class OutputGenerator(object):
    def __init__(self, argv, sentence_imgs, sentence, commandgroup):
        """Generates the HTML output as to be analysed.

        Args:
            argv: The command line arguments.
            sentence_imgs: A list of all the sentence images (string path), one for each sentence.
            sentence: A list of all the sentences (string raw text).
            commandgroup: the CommandGroup object itself, as to access the current groups of sentences.
        """
        self.argv = argv
        self.sentence_imgs = sentence_imgs
        self.sentence = sentence
        self.groups = commandgroup.get_groups()
        self.commandgroup = commandgroup

    def graph_gen_html(self):
        """Generates the HTML output as to be analysed.
        """
        setup_django_template_system()
        file_name = "results-" + self.argv.tetre_word + ".html"

        with open(dirs['html_templates']['path'] + 'index_group.html', 'r') as index_group:
            index_group = index_group.read()

        with open(dirs['html_templates']['path'] + 'each_img.html', 'r') as each_img:
            each_img = each_img.read()

        with open(dirs['html_templates']['path'] + 'each_img_accumulator.html', 'r') as each_img_accumulator:
            each_img_accumulator = each_img_accumulator.read()

        i = 0

        all_imgs_html = ""
        max_sentences = 0

        for group in group_sorting(self.groups):

            t = Template(each_img_accumulator)
            c = Context({"accumulator_img": group["img"],
                         "total_group_sentences": len(group["sentences"])})
            all_imgs_html += t.render(c)

            each_img_html = ""

            if len(group["sentences"]) > max_sentences:
                max_sentences = len(group["sentences"])

            for sentence in group["sentences"]:
                t = Template(each_img)
                c = Context({"gf_id": sentence["sentence"].file_id,
                             "gs_id": sentence["sentence"].id,
                             "gt_id": sentence["token"].idx,
                             "path": sentence["img_path"],
                             "sentence": mark_safe(highlight_word(sentence["sentence"], self.argv.tetre_word))})
                each_img_html += t.render(c)

                i += 1

            all_imgs_html += each_img_html

        avg_per_group = self.commandgroup.get_average_per_group()
        max_num_params = self.commandgroup.get_max_params()

        t = Template(index_group)
        c = Context({"sentences_num": len(self.sentence),
                     "groups_num": len(self.groups),
                     "max_group_num": max_sentences,
                     "average_per_group": avg_per_group,
                     "all_sentences": mark_safe(all_imgs_html),
                     "max_num_params": max_num_params,
                     "word": self.argv.tetre_word})

        with open(dirs['output_html']['path'] + file_name, 'w') as output:
            output.write(t.render(c))


class CommandGroup(SentencesAccumulator, ResultsGroupMatcher):
    def __init__(self, argv):
        """Generates the HTML for all sentences containing the searched word. It groups the sentences based on the
        child nodes of the token with the word being searched. No rules are applied so sentences are presented as is.

        Args:
            argv: The command line arguments.
        """
        SentencesAccumulator.__init__(self, argv)
        ResultsGroupMatcher.__init__(self, argv)

        self.img_renderer = GroupImageRenderer(argv)
        self.argv = argv

    def group_accounting_add_by_token(self, tree, token, sentence, img_path):
        """Groups the sentences based on the child nodes of the token with the word being searched.

        Args:
            tree: The NLTK tree with the node representation.
            token: The TreeNode SpaCy-like node.
            sentence: The raw sentence text.
            img_path: The path to the image related to this sentence.
        """
        self.group_accounting_add(tree, token, sentence, img_path, token, self.img_renderer)

    def run(self):
        """Execution entry point.
        """
        for token, sentence in get_tokens(self.argv):
            img_path = self.process_sentence(sentence)

            tree = get_node_representation(self.argv.tetre_format, token)

            self.group_accounting_add_by_token(tree, token, sentence, img_path)

        output_generator = OutputGenerator(self.argv,
                                           self.sentence_imgs,
                                           self.sentence,
                                           self)
        output_generator.graph_gen_html()
