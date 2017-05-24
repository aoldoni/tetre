from graphviz import Digraph

import operator
from functools import reduce

from django.utils.safestring import mark_safe
from django.template import Template, Context

from tetre.command_utils import setup_django_template_system
from tetre.command import SentencesAccumulator, GroupImageNameGenerator

from directories import dirs

from tree_utils import get_token_representation
from parsers import get_tokens


accumulated_print_each = 10


class GroupImageRenderer(object):
    base_image_name = 'accumulated'

    def __init__(self, argv):
        """Generates the images for each group of sentences.

        Args:
            argv: The command line arguments.
        """
        self.argv = argv

    def graph_gen_generate(self, accumulator_parents, accumulator_children, image_id=""):
        """Generates the images based on the accumulated data from the nodes that represents this group.

        Args:
            accumulator_parents: All accumulated parent nodes for the token being searched.
            accumulator_children: All accumulated child nodes for the token being searched.
            image_id: An integer with the current group id.

        Returns:
            A string with the image path.
        """

        e = Digraph(self.argv.tetre_word, format=GroupImageNameGenerator.file_extension)
        e.attr('node', shape='box')

        main_node = "A"

        e.node(main_node, self.argv.tetre_word)

        total_len_accumulator_children = reduce(lambda a, b: a+b,
                                                (len(value) for key, value in accumulator_children.items()),
                                                0)

        i = 0
        for key, value in accumulator_children.items():
            percentage = (100 * len(value)) / total_len_accumulator_children
            sorted_values = sorted(value.items(), key=operator.itemgetter(1))
            e.node(str(i), "\n".join([value[0] for value in sorted_values]))
            e.edge(main_node, str(i), label=key, xlabel="{0:.2f}%".format(percentage))

            i += 1

        total_len_accumulator_parents = reduce(lambda a, b: a+b,
                                               (len(value) for key, value in accumulator_parents.items()),
                                               0)

        for key, value in accumulator_parents.items():
            percentage = (100 * len(value)) / total_len_accumulator_parents
            sorted_values = sorted(value.items(), key=operator.itemgetter(1))
            e.node(str(i), "\n".join([value[0] for value in sorted_values]))
            e.edge(str(i), main_node, label=key, xlabel="{0:.2f}%".format(percentage))

            i += 1

        name_generator = GroupImageNameGenerator(self.base_image_name, self.argv.tetre_word, image_id)
        e.render(name_generator.get_render_path())

        return name_generator.get_base_path_with_extension()


class OutputGenerator(object):
    def __init__(self, argv, sentence_accumulated_each_imgs, sentence_imgs, sentence):
        """Generates the HTML output as to be analysed.

        Args:
            argv: The command line arguments.
            sentence_accumulated_each_imgs: A list of the groups images (string path).
            sentence_imgs: A list of all the sentences (string raw text).
            sentence: The list of raw sentences string.
        """
        self.argv = argv
        self.sentence_accumulated_each_imgs = sentence_accumulated_each_imgs
        self.sentence_imgs = sentence_imgs
        self.sentence = sentence

    def graph_gen_html(self):
        """Generates the HTML output as to be analysed.
        """
        setup_django_template_system()
        file_name = "results-" + self.argv.tetre_word + ".html"

        with open(dirs['html_templates']['path'] + 'index.html', 'r') as index:
            index = index.read()

        with open(dirs['html_templates']['path'] + 'each_img.html', 'r') as each_img:
            each_img = each_img.read()

        with open(dirs['html_templates']['path'] + 'each_img_accumulator.html', 'r') as each_img_accumulator:
            each_img_accumulator = each_img_accumulator.read()

        last_img = 0
        all_imgs_html = ""
        for i in range(0, len(self.sentence_accumulated_each_imgs)):

            next_img = min(last_img + accumulated_print_each, len(self.sentence_imgs))

            t = Template(each_img_accumulator)
            c = Context({"accumulator_img": self.sentence_accumulated_each_imgs[i],
                         "total_group_sentences": (next_img-last_img)})

            all_imgs_html += t.render(c)
            each_img_html = ""
            
            for j in range(last_img, next_img):
                t = Template(each_img)
                c = Context({"gf_id": '',
                             "gs_id": '',
                             "gt_id": '',
                             "path": self.sentence_imgs[j],
                             "sentence": self.sentence[j]})
                each_img_html += t.render(c)

                last_img = next_img

            all_imgs_html += each_img_html

        name_generator = GroupImageNameGenerator(GroupImageRenderer.base_image_name, self.argv.tetre_word)

        t = Template(index)
        c = Context({"main_img": name_generator.get_base_path_with_extension(),
                     "all_sentences": mark_safe(all_imgs_html),
                     "word": self.argv.tetre_word})

        with open(dirs['output_html']['path'] + file_name, 'w') as output:
            output.write(t.render(c))


class CommandAccumulative(SentencesAccumulator):
    def __init__(self, argv):
        """Generates the HTML for all sentences containing the searched word. It does not group the sentences
        based on any logic, except their order. Every X sentences (determined by the accumulated_print_each module
        variable) get grouped, and the sorrounding nodes of the token being searched for in these sentences
        get accumulated for statistics. It is useful in case one wants to find the most common dependencies
        for this word.

        Args:
            argv: The command line arguments.
        """
        SentencesAccumulator.__init__(self, argv)

        self.accumulated_children = {}
        self.accumulated_parents = {}

        self.accumulated_children_local = {}
        self.accumulated_parents_local = {}

        self.main_image = ""
        self.sentence_accumulated_each_imgs = []

    def graph_gen_accumulate(self, token, accumulator_parents, accumulator_children):
        """Given a node in the tree, obtain the sorrounding nodes and accumulate them for statistics.

        Args:
            token: The TreeNode SpaCy-like node.
            accumulator_parents: All accumulated parent nodes for the token being searched.
            accumulator_children: All accumulated child nodes for the token being searched.
        """
        if token.dep_.strip() != "":
            if token.dep_ not in accumulator_parents:
                accumulator_parents[token.dep_] = {}

            strip_string = get_token_representation(self.argv.tetre_format, token.head)
            if strip_string != "":
                if strip_string not in accumulator_parents[token.dep_]:
                    accumulator_parents[token.dep_][strip_string] = 1
                else:
                    accumulator_parents[token.dep_][strip_string] += 1

        for child in token.children:
            if child.dep_.strip() == "":
                continue

            if child.dep_ not in accumulator_children:
                accumulator_children[child.dep_] = {}

            strip_string = get_token_representation(self.argv.tetre_format, child)

            if strip_string == "":
                continue

            if strip_string not in accumulator_children[child.dep_]:
                accumulator_children[child.dep_][strip_string] = 1
            else:
                accumulator_children[child.dep_][strip_string] += 1

    def run(self):
        """Execution entry point.
        """
        accumulated_global_count = 0
        accumulated_local_count = 0

        img_renderer = GroupImageRenderer(self.argv)

        for token, sentence in get_tokens(self.argv):

            self.process_sentence(sentence)
            self.graph_gen_accumulate(token, self.accumulated_parents, self.accumulated_children)
            self.graph_gen_accumulate(token, self.accumulated_parents_local, self.accumulated_children_local)

            if accumulated_print_each == accumulated_local_count:
                self.sentence_accumulated_each_imgs.append(
                    img_renderer.graph_gen_generate(
                        self.accumulated_parents_local,
                        self.accumulated_children_local,
                        str(accumulated_global_count))
                )
                accumulated_global_count += 1

                accumulated_local_count = 0
                self.accumulated_children_local = {}
                self.accumulated_parents_local = {}

            else:
                accumulated_local_count += 1

        output_generator = OutputGenerator(self.argv,
                                           self.sentence_accumulated_each_imgs,
                                           self.sentence_imgs,
                                           self.sentence)

        self.main_image = img_renderer.graph_gen_generate(self.accumulated_parents, self.accumulated_children)
        output_generator.graph_gen_html()
