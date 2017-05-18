from graphviz import Digraph
from nltk import Tree

from django.utils.safestring import mark_safe
from django.template import Template, Context

from tetre.command_utils import setup_django_template_system
from tetre.command import SentencesAccumulator, ResultsGroupMatcher

from directories import dirs
from parsers import get_tokens, highlight_word
from tree_utils import to_nltk_tree_general, group_sorting, get_node_representation


class CommandGroup(SentencesAccumulator, ResultsGroupMatcher):
    def __init__(self, argv):
        SentencesAccumulator.__init__(self, argv)
        ResultsGroupMatcher.__init__(self, argv)

        self.argv = argv

        self.take_pos_into_consideration = len(
            [params for params in self.argv.tetre_format.split(",") if params == "pos_"])

    def run(self):
        for token, sentence in get_tokens(self.argv):
            img_path = self.process_sentence(sentence)

            tree = get_node_representation(self.argv.tetre_format, token)

            self.group_accounting_add_by_token(tree, token, sentence, img_path)

        self.graph_gen_html()

        return

    def gen_group_image(self, token, depth = 1):
        e = Digraph(self.argv.tetre_word, format=self.file_extension)
        e.attr('node', shape='box')

        current_id = self.current_token_id
        e.node(str(current_id), token.pos_)

        self.group_to_graph_recursive_with_depth(token, current_id, e, depth)

        img_name = 'command-group-' + self.argv.tetre_word + "-" + str(self.current_group_id)
        e.render(self.output_path + 'images/' + img_name)
        self.current_group_id += 1
        return 'images/' + img_name + "." + self.file_extension

    def group_to_graph_recursive_with_depth(self, token, parent_id, e, depth):
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

        return

    def graph_gen_html(self):
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

        avg_per_group = self.get_average_per_group()
        max_num_params = self.get_max_params()

        t = Template(index_group)
        c = Context({"sentences_num": len(self.sentence),
                     "groups_num": len(self.groups),
                     "max_group_num": max_sentences,
                     "average_per_group": avg_per_group,
                     "all_sentences": mark_safe(all_imgs_html),
                     "max_num_params": max_num_params,
                     "word": self.argv.tetre_word})

        with open(self.output_path + file_name, 'w') as output:
            output.write(t.render(c))

        return
