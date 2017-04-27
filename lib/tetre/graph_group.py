from graphviz import Digraph

import django
from django.utils.safestring import mark_safe
from django.template import Template, Context
from django.conf import settings

from tree_utils import *
from directories import dirs

from tetre.graph import CommandAccumulative
from tetre.dependency_helpers import *


class CommandGroup(CommandAccumulative):
    def __init__(self, argv):
        CommandAccumulative.__init__(self, argv)
        self.argv = argv
        self.groups = {}

        self.depth = 1
        self.current_group_id = 0

        self.take_pos_into_consideration = len(
            [params for params in self.argv.tetre_format.split(",") if params == "pos_"])

    def run(self):
        for token, sentence in get_tokens(self.argv):
            img_path = self.process_sentence(sentence)

            tree = self.get_node_representation(token)

            self.group_accounting_add(tree, token, sentence, img_path)

        self.main_image = self.graph_gen_generate(self.accumulated_parents, self.accumulated_children)
        self.graph_gen_html()

        return

    def get_node_representation(self, token):

        params = self.argv.tetre_format.split(",")

        node_representation = token.pos_
        if token.n_lefts + token.n_rights > 0:
            tree = Tree(node_representation,
                        [to_nltk_tree_general(child, attr_list=params, level=0) for child in token.children])
        else:
            tree = Tree(node_representation, [])

        return tree

    def group_accounting_add(self, tree, token, sentence, img_path):
        string = nltk_tree_to_qtree(tree)

        if string in self.groups:
            group = self.groups[string]

            group["sentences"].append({"sentence": sentence, "token": token, "img_path": img_path})
        else:
            self.groups[string] = {"representative": tree,
                                   "img": self.gen_group_image(token, tree, self.depth),
                                   "sentences": [
                                       {"sentence": sentence, "token": token, "img_path": img_path}
                                       ]}

    def gen_group_image(self, token, tree, depth):
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

    def get_average_per_group(self):
        return int(self.get_sentence_totals() / len(self.groups))

    def get_max_params(self):
        max_params = 0

        for group in self.groups.values():
            if group["params"] > max_params:
                max_params = group["params"]

        return max_params

    def get_sentence_totals(self):
        total = 0

        for key, group in self.groups.items():
            total += len(group["sentences"])

        return total

    def percentage(self, percent, whole):
        return (percent * whole) / 100.0

    def graph_gen_html(self):
        settings.configure()
        settings.TEMPLATES = [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates'
            }
        ]
        django.setup()

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

        with open(self.output_path + self.file_name, 'w') as output:
            output.write(t.render(c))

        return
