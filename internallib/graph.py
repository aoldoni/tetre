from graphviz import Digraph

import spacy
import spacy.en

import itertools
import operator

import django
from django.utils.safestring import mark_safe
from django.template import Template, Context
from django.conf import settings

from functools import reduce
import pprint

from internallib.dependency_helpers import *
from internallib.directories import *

from internallib.graph_processing import Process

class CommandAccumulative(object):
    def __init__(self, args):
        self.args = args

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

        self.output_path = self.args.directory+output_html

    def run(self):

        accumulated_global_count = 0
        accumulated_local_count = 0

        for token, sentence in get_tokens(self.args):
            self.process_sentence(sentence)
            self.graph_gen_accumulate(token, self.accumulated_parents, self.accumulated_children)
            self.graph_gen_accumulate(token, self.accumulated_parents_local, self.accumulated_children_local)

            if (self.accumulated_print_each == accumulated_local_count):
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
        # return str(token).strip()

        string_representation = []
        params = self.args.format.split(",")
        for param in params:
            string_representation.append(getattr(token, param))

        return "/".join(string_representation)
        # sys.exit()

    def process_sentence(self, sentence):
        self.sentence.append(str(sentence).replace("\r","").replace("\n","").strip())
        return self.sentence_to_graph(sentence)

    def graph_gen_accumulate(self, token, accumulator_parents, accumulator_children):

        if token.dep_.strip() != "":
            if (token.dep_ not in accumulator_parents):
                accumulator_parents[token.dep_] = {}

            strip_string = self.get_token_representation(token.head)
            if strip_string != "":
                if (strip_string not in accumulator_parents[token.dep_]):
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
        e = Digraph(self.args.word, format=self.file_extension)
        e.attr('node', shape='box')

        main_node = "A"

        e.node(main_node, self.args.word)

        total_len_accumulator_children = reduce(lambda a,b: a+b, (len(value) for key, value in accumulator_children.items()), 0)

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

    def sentence_to_graph(self, sentence):
        e = Digraph(self.args.word, format='png')
        e.attr('node', shape='box')

        current_id = self.current_token_id
        e.node(str(current_id), sentence.root.orth_)

        self.sentence_to_graph_recursive(sentence.root, current_id, e)

        img_name = 'sentence-'+str(self.current_sentence_id)
        img_path = 'images/' + img_name + "." + self.file_extension
        self.sentence_imgs.append(img_path)

        e.render(self.output_path + 'images/' + img_name)

        self.current_sentence_id += 1

        return img_path

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

        index = ""
        each_img_accumulator = ""
        each_img = ""

        with open(html_templates + 'index.html', 'r') as index:
            index = index.read()

        with open(html_templates + 'each_img.html', 'r') as each_img:
            each_img = each_img.read()

        with open(html_templates + 'each_img_accumulator.html', 'r') as each_img_accumulator:
            each_img_accumulator = each_img_accumulator.read()

        last_img = 0
        all_imgs_html = ""
        for i in range(0, len(self.sentence_accumulated_each_imgs)):
            t = Template(each_img_accumulator)
            c = Context({"accumulator_img": self.sentence_accumulated_each_imgs[i]})
            all_imgs_html += t.render(c)

            each_img_html = ""

            next_img = min(last_img + self.accumulated_print_each, len(self.sentence_imgs))
            for i in range(last_img, next_img):
                t = Template(each_img)
                c = Context({"s_id": i,
                             "path": self.sentence_imgs[i],
                             "sentence": self.sentence[i]})
                each_img_html += t.render(c)

                last_img = next_img

            all_imgs_html += each_img_html

        t = Template(index)
        c = Context({"main_img": "images/main_image.png",
                     "all_sentences": mark_safe(all_imgs_html),
                     "word": self.args.word})

        with open(self.output_path + 'results.html', 'w') as output:
            output.write(t.render(c))

        return



class CommandGroup(CommandAccumulative):
    def __init__(self, args):
        CommandAccumulative.__init__(self, args)
        self.args = args
        self.groups = []

        self.depth = 1

        self.take_pos_into_consideration = len([params for params in self.args.format.split(",") if params == "pos_"])

    def run(self):

        rule_applier = Process()
        params = self.args.format.split(",")

        for token, sentence in get_tokens(self.args):
            img_path = self.process_sentence(sentence)

            # print("TOKEN - ", token.pos_, token.n_lefts, token.n_rights, list(token.children))

            node_representation = token.pos_
            if token.n_lefts + token.n_rights > 0:
                tree = Tree(node_representation, [to_nltk_tree_general(child, attr_list=params, level=0) for child in token.children])
            else:
                tree = Tree(node_representation, [])

            self.group_accounting_add(tree, token, sentence, img_path)

        self.main_image = self.graph_gen_generate(self.accumulated_parents, self.accumulated_children)
        self.graph_gen_html()

        return

    def group_accounting_add(self, tree, token, sentence, img_path):
        found = False

        for group in self.groups:
            if (group["representative"] == tree):
                group["sum"] = group["sum"] + 1
                group["sentences"].append({"sentence" : sentence, "token" : token, "img_path" : img_path})
                found = True
                break

        if (not found):
            self.groups.append({"representative" : tree, \
                "sum" : 1, \
                "img" : self.gen_group_image(token, tree, self.depth), \
                "sentences" : [ \
                    {"sentence" : sentence, "token" : token, "img_path" : img_path} \
                ]})

    def gen_group_image(self, token, tree, depth):
        e = Digraph(self.args.word, format='png')
        e.attr('node', shape='box')

        current_id = self.current_token_id
        e.node(str(current_id), token.pos_)

        self.sentence_to_graph_recursive_with_depth(token, current_id, e, depth)

        img_name = 'sentence-'+str(self.current_sentence_id)

        e.render(self.output_path + 'images/' + img_name)

        self.current_sentence_id += 1

        return 'images/' + img_name + "." + self.file_extension

    def sentence_to_graph_recursive_with_depth(self, token, parent_id, e, depth):

        if len(list(token.children)) == 0 or depth == 0:
            return

        current_global_id = {}

        for child in token.children:
            self.current_token_id = self.current_token_id + 1
            current_global_id[str(self.current_token_id)] = child

        for child_id, child in current_global_id.items():
            if (self.take_pos_into_consideration):
                e.node(child_id, child.pos_)
            else:
                e.node(child_id, "???")
            e.edge(str(parent_id), child_id, label=child.dep_)

        for child_id, child in current_global_id.items():
            self.sentence_to_graph_recursive_with_depth(child, child_id, e, depth-1)

        return

    def graph_gen_html(self):
        settings.configure()
        settings.TEMPLATES = [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates'
            }
        ]
        django.setup()

        index_group = ""
        each_img_accumulator = ""
        each_img = ""

        with open(html_templates + 'index_group.html', 'r') as index_group:
            index_group = index_group.read()

        with open(html_templates + 'each_img.html', 'r') as each_img:
            each_img = each_img.read()

        with open(html_templates + 'each_img_accumulator.html', 'r') as each_img_accumulator:
            each_img_accumulator = each_img_accumulator.read()

        i = 0

        all_imgs_html = ""

        # pprint.pprint(group_sorting(self.groups))

        for group in group_sorting(self.groups):

            t = Template(each_img_accumulator)
            c = Context({"accumulator_img": group["img"]})
            all_imgs_html += t.render(c)

            each_img_html = ""

            for sentence in group["sentences"]:
                t = Template(each_img)
                c = Context({"s_id": i,
                             "path": sentence["img_path"],
                             "sentence": sentence["sentence"]})
                each_img_html += t.render(c)

                i += 1

            all_imgs_html += each_img_html

        t = Template(index_group)
        c = Context({"all_sentences": mark_safe(all_imgs_html),
                     "word": self.args.word})

        with open(self.output_path+'results.html', 'w') as output:
            output.write(t.render(c))

        return



class CommandSimplifiedGroup(CommandGroup):
    def __init__(self, args):
        CommandGroup.__init__(self, args)

    def run(self):

        rule_applier = Process()
        params = self.args.format.split(",")

        for token, sentence in get_tokens(self.args):
            img_path = self.process_sentence(sentence)

            # print("TOKEN - ", token.pos_, token.n_lefts, token.n_rights, list(token.children))

            node_representation = token.pos_
            if token.n_lefts + token.n_rights > 0:
                tree = Tree(node_representation, [to_nltk_tree_general(child, attr_list=params, level=0) for child in token.children])
            else:
                tree = Tree(node_representation, [])

            tree = rule_applier.applyAll(tree, token)
            self.group_accounting_add(tree, token, sentence, img_path)

        self.main_image = self.graph_gen_generate(self.accumulated_parents, self.accumulated_children)
        self.graph_gen_html()

    def gen_group_image(self, token, tree, depth):
        e = Digraph(self.args.word, format='png')
        e.attr('node', shape='box')

        current_id = self.current_token_id
        e.node(str(current_id), tree.label())

        current_global_id = {}

        for child in tree:
            self.current_token_id = self.current_token_id + 1
            current_global_id[str(self.current_token_id)] = child

        for child_id, child in current_global_id.items():
            e.node(child_id, "???")
            e.edge(str(current_id), child_id, label=child)

        img_name = 'sentence-'+str(self.current_sentence_id)
        e.render(self.output_path + 'images/' + img_name)
        self.current_sentence_id += 1
        return 'images/' + img_name + "." + self.file_extension