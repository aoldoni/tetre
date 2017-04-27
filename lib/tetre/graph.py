from graphviz import Digraph

import operator
from functools import reduce

import django
from django.utils.safestring import mark_safe
from django.template import Template, Context
from django.conf import settings

from tree_utils import *

from directories import dirs
from cache import get_cached_sentence_image

from tetre.dependency_helpers import *


class CommandAccumulative(object):
    def __init__(self, argv):
        self.argv = argv

        self.accumulated_children = {}
        self.accumulated_parents = {}

        self.accumulated_children_local = {}
        self.accumulated_parents_local = {}

        self.current_sentence_id = 0
        self.current_token_id = 0

        self.main_image = ""
        self.sentence_accumulated_each_imgs = []
        self.sentence_imgs = []
        self.sentence = []

        self.accumulated_print_each = 10
        self.file_extension = "png"

        self.output_path = dirs['output_html']['path']
        self.file_name = "results-" + argv.tetre_word + ".html"

    def run(self):
        accumulated_global_count = 0
        accumulated_local_count = 0

        for token, sentence in get_tokens(self.argv):

            self.process_sentence(sentence)
            self.graph_gen_accumulate(token, self.accumulated_parents, self.accumulated_children)
            self.graph_gen_accumulate(token, self.accumulated_parents_local, self.accumulated_children_local)

            if self.accumulated_print_each == accumulated_local_count:
                self.sentence_accumulated_each_imgs.append(
                    self.graph_gen_generate(
                        self.accumulated_parents_local,
                        self.accumulated_children_local,
                        str(accumulated_global_count)) + "." + self.file_extension
                )
                accumulated_global_count += 1

                accumulated_local_count = 0
                self.accumulated_children_local = {}
                self.accumulated_parents_local = {}

            else:
                accumulated_local_count += 1            

        self.main_image = self.graph_gen_generate(self.accumulated_parents, self.accumulated_children)
        self.graph_gen_html()

        return

    def get_token_representation(self, token):
        string_representation = []
        params = self.argv.tetre_format.split(",")
        for param in params:
            string_representation.append(getattr(token, param))

        return "/".join(string_representation)

    def process_sentence(self, sentence):
        self.sentence.append(str(sentence).replace("\r", "").replace("\n", "").strip())
        if self.argv.tetre_output == "html":
            return self.sentence_to_graph(sentence)
        else:
            return ""

    def graph_gen_accumulate(self, token, accumulator_parents, accumulator_children):
        if token.dep_.strip() != "":
            if token.dep_ not in accumulator_parents:
                accumulator_parents[token.dep_] = {}

            strip_string = self.get_token_representation(token.head)
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

            strip_string = self.get_token_representation(child)

            if strip_string == "":
                continue

            if strip_string not in accumulator_children[child.dep_]:
                accumulator_children[child.dep_][strip_string] = 1
            else:
                accumulator_children[child.dep_][strip_string] += 1

        return

    def graph_gen_generate(self, accumulator_parents, accumulator_children, id = ""):
        e = Digraph(self.argv.tetre_word, format=self.file_extension)
        e.attr('node', shape='box')

        main_node = "A"

        e.node(main_node, self.argv.tetre_word)

        total_len_accumulator_children = reduce(lambda a, b: a+b, (len(value) for key, value in accumulator_children.items()), 0)

        i = 0
        for key, value in accumulator_children.items():
            percentage = (100 * len(value)) / total_len_accumulator_children
            sorted_values = sorted(value.items(), key=operator.itemgetter(1))
            e.node(str(i), "\n".join([value[0] for value in sorted_values]))
            e.edge(main_node, str(i), label=key, xlabel="{0:.2f}%".format(percentage))

            i += 1

        total_len_accumulator_parents = reduce(lambda a,b: a+b, (len(value) for key, value in accumulator_parents.items()), 0)

        for key, value in accumulator_parents.items():
            percentage = (100 * len(value)) / total_len_accumulator_parents
            sorted_values = sorted(value.items(), key=operator.itemgetter(1))
            e.node(str(i), "\n".join([value[0] for value in sorted_values]))
            e.edge(str(i), main_node, label=key, xlabel="{0:.2f}%".format(percentage))

            i += 1

        e.render(self.output_path + 'images/main_image' + id)

        return 'images/main_image' + id

    def sentence_to_graph_add_node(self, e, current_id, orth_):
        if orth_ == self.argv.tetre_word:
            e.node(str(current_id), orth_, fillcolor="dimgrey", fontcolor="white", style="filled")
        else:
            e.node(str(current_id), orth_)

    def sentence_to_graph(self, sentence):
        img_name = 'sentence-'+str(sentence.file_id)+"-"+str(sentence.id)
        img_dot_path = 'images/' + img_name
        img_path = img_dot_path + "." + self.file_extension
        self.sentence_imgs.append(img_path)

        found = get_cached_sentence_image(self.argv,
                                            self.output_path,
                                            sentence,
                                            self.file_extension)

        if not found:
            e = Digraph(self.argv.tetre_word, format=self.file_extension)
            e.attr('node', shape='box')
            e.attr('graph', label=str(sentence))

            current_id = self.current_token_id
            self.sentence_to_graph_add_node(e, current_id, sentence.root.orth_)
            self.sentence_to_graph_recursive(sentence.root, current_id, e)
            e.render(self.output_path + img_dot_path)
        
        self.current_sentence_id += 1

        return img_path

    def sentence_to_graph_recursive(self, token, parent_id, e):
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

        return

    def graph_gen_html(self):
        settings.configure()
        settings.TEMPLATES = [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates'
            }
        ]
        django.setup()

        with open(dirs['html_templates']['path'] + 'index.html', 'r') as index:
            index = index.read()

        with open(dirs['html_templates']['path'] + 'each_img.html', 'r') as each_img:
            each_img = each_img.read()

        with open(dirs['html_templates']['path'] + 'each_img_accumulator.html', 'r') as each_img_accumulator:
            each_img_accumulator = each_img_accumulator.read()

        last_img = 0
        all_imgs_html = ""
        for i in range(0, len(self.sentence_accumulated_each_imgs)):

            next_img = min(last_img + self.accumulated_print_each, len(self.sentence_imgs))

            t = Template(each_img_accumulator)
            c = Context({"accumulator_img": self.sentence_accumulated_each_imgs[i],
                         "total_group_sentences" : (next_img-last_img)})

            all_imgs_html += t.render(c)
            each_img_html = ""
            
            for i in range(last_img, next_img):
                t = Template(each_img)
                c = Context({"gf_id": sentence["sentence"].file_id,
                             "gs_id": sentence["sentence"].id,
                             "gt_id": sentence["token"].idx,
                             "path": self.sentence_imgs[i],
                             "sentence": self.sentence[i]})
                each_img_html += t.render(c)

                last_img = next_img

            all_imgs_html += each_img_html

        t = Template(index)
        c = Context({"main_img": "images/main_image." + self.file_extension,
                     "all_sentences": mark_safe(all_imgs_html),
                     "word": self.argv.tetre_word})

        with open(self.output_path + self.file_name, 'w') as output:
            output.write(t.render(c))

        return
