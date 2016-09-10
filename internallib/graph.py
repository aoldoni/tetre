from graphviz import Digraph

import spacy
import spacy.en

import itertools
import operator

import django
from django.utils.safestring import mark_safe
from django.template import Template, Context
from django.conf import settings

from internallib.dependency_helpers import *

class Command(object):
    def __init__(self, args):
        self.args = args
        self.accumulated_children = {}
        self.accumulated_parents = {}

        self.current_sentence_id = 0
        self.current_token_id = 0
        self.sentence_imgs = []
        self.sentence = []

        self.max = 9999999999
        self.current = 0
        self.total = 0

    def get_representation(self, token):
        # return str(token).strip()

        string_representation = []
        params = self.args.format.split(",")
        for param in params:
            string_representation.append(getattr(token, param))

        return "/".join(string_representation)
        # sys.exit()

    def run(self):

        for token, sentence in get_tokens(self.args):
            self.process_sentence(sentence)
            self.graph_gen_accumulate(token)

        self.graph_gen_generate()
        self.graph_gen_html()

        sys.exit()

    def process_sentence(self, sentence):
        self.sentence.append(str(sentence).replace("\r","").replace("\n","").strip())
        self.sentence_to_graph(sentence)

    def graph_gen_accumulate(self, token):

        if token.dep_.strip() != "":
            if (token.dep_ not in self.accumulated_parents):
                self.accumulated_parents[token.dep_] = {}

            strip_string = self.get_representation(token.head)
            if strip_string != "":
                if (strip_string not in self.accumulated_parents[token.dep_]):
                    self.accumulated_parents[token.dep_][strip_string] = 1
                else:
                    self.accumulated_parents[token.dep_][strip_string] += 1

        for child in token.children:
            if child.dep_.strip() == "":
                continue

            if child.dep_ not in self.accumulated_children:
                self.accumulated_children[child.dep_] = {}

            strip_string = self.get_representation(child)

            if strip_string == "":
                continue

            if strip_string not in self.accumulated_children[child.dep_]:
                self.accumulated_children[child.dep_][strip_string] = 1
            else:
                self.accumulated_children[child.dep_][strip_string] += 1

            self.current += 1

        return

    def graph_gen_generate(self):
        e = Digraph(self.args.word, format='png')
        e.attr('node', shape='box')

        main_node = "A"

        e.node(main_node, self.args.word)

        i = 0
        for key, value in self.accumulated_children.items():
            sorted_values = sorted(value.items(), key=operator.itemgetter(1))
            e.node(str(i), "\n".join([value[0] for value in sorted_values]))
            e.edge(main_node, str(i), label=key)

            i += 1

        for key, value in self.accumulated_parents.items():
            sorted_values = sorted(value.items(), key=operator.itemgetter(1))
            e.node(str(i), "\n".join([value[0] for value in sorted_values]))
            e.edge(str(i), main_node, label=key)

            i += 1

        e.render('output/html/images/main_image')

        self.total += 1

        return

    def sentence_to_graph(self, sentence):
        e = Digraph(self.args.word, format='png')
        e.attr('node', shape='box')

        current_id = self.current_token_id
        e.node(str(current_id), sentence.root.orth_)

        self.sentence_to_graph_recursive(sentence.root, current_id, e)

        img_name = 'sentence-'+str(self.current_sentence_id)
        self.sentence_imgs.append('images/' + img_name + ".png")

        e.render('output/html/images/' + img_name)

        self.current_sentence_id += 1

        return

    def sentence_to_graph_recursive(self, token, parent_id, e):

        if len(list(token.children)) == 0:
            return

        current_global_id = {}

        for child in token.children:
            self.current_token_id = self.current_token_id + 1
            current_global_id[str(self.current_token_id)] = child

        for child_id, child in current_global_id.items():
            e.node(child_id, child.orth_)
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

        template = ""
        each_img = ""

        with open('output/templates/index.html', 'r') as index:
            template = index.read()

        with open('output/templates/each_img.html', 'r') as each_img:
            each_img = each_img.read()

        each_img_html = ""
        for i in range(0, len(self.sentence_imgs)):
            t = Template(each_img)
            c = Context({"path": self.sentence_imgs[i],
                         "sentence": self.sentence[i]})
            each_img_html += t.render(c)

        t = Template(template)
        c = Context({"main_img": "images/main_image.png",
                     "all_sentences": mark_safe(each_img_html)})

        with open('output/html/results.html', 'w') as output:
            output.write(t.render(c))

        return
