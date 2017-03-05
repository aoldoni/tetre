from graphviz import Digraph

import operator
import json
import copy
from functools import reduce
import random
import csv

import django
from django.utils.safestring import mark_safe
from django.template import Template, Context
from django.conf import settings

from tree_utils import *

from directories import dirs
from cache import get_cached_sentence_image

from tetre.graph_processing import Process, Reduction
from tetre.graph_processing_children import ProcessChildren
from tetre.graph_extraction import ProcessExtraction
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
        string_representation = []
        params = self.argv.tetre_format.split(",")
        for param in params:
            string_representation.append(getattr(token, param))

        return "/".join(string_representation)
        # sys.exit()

    def process_sentence(self, sentence):
        self.sentence.append(str(sentence).replace("\r","").replace("\n","").strip())
        if self.argv.tetre_output == "html":
            return self.sentence_to_graph(sentence)
        else:
            return ""

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
        e = Digraph(self.argv.tetre_word, format=self.file_extension)
        e.attr('node', shape='box')

        main_node = "A"

        e.node(main_node, self.argv.tetre_word)

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

    def sentence_to_graph_add_node(self, e, current_id, orth_):
        if (orth_ == self.argv.tetre_word):
            e.node(str(current_id), orth_, fillcolor="dimgrey", fontcolor="white", style="filled")
        else:
            e.node(str(current_id), orth_)

    def sentence_to_graph(self, sentence):
        img_name = 'sentence-'+str(sentence.file_id)+"-"+str(sentence.id)
        img_dot_path = 'images/' + img_name
        img_path = img_dot_path + "." + self.file_extension
        self.sentence_imgs.append(img_path)

        found = get_cached_sentence_image(self.argv, \
                                            self.output_path, \
                                            sentence, \
                                            self.file_extension)

        if (not found):
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
            self.current_token_id = self.current_token_id + 1
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

            next_img = min(last_img + self.accumulated_print_each, len(self.sentence_imgs))

            t = Template(each_img_accumulator)
            c = Context({"accumulator_img": self.sentence_accumulated_each_imgs[i], \
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



class CommandGroup(CommandAccumulative):
    def __init__(self, argv):
        CommandAccumulative.__init__(self, argv)
        self.argv = argv
        self.groups = {}

        self.depth = 1
        self.current_group_id = 0

        self.take_pos_into_consideration = len([params for params in self.argv.tetre_format.split(",") if params == "pos_"])

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
        # node_representation = token.dep_+"/"+token.pos_
        if token.n_lefts + token.n_rights > 0:
            tree = Tree(node_representation, [to_nltk_tree_general(child, attr_list=params, level=0) for child in token.children])
        else:
            tree = Tree(node_representation, [])

        return tree

    def group_accounting_add(self, tree, token, sentence, img_path):
        found = False

        string = nltk_tree_to_qtree(tree)
        # string2 = treenode_to_qtree(token)

        if (string in self.groups):
            group = self.groups[string]

            # group["sum"] = group["sum"] + 1
            group["sentences"].append({"sentence" : sentence, "token" : token, "img_path" : img_path})
        else:
            self.groups[string] = {"representative" : tree, \
                # "sum" : 1, \
                "img" : self.gen_group_image(token, tree, self.depth), \
                "sentences" : [ \
                    {"sentence" : sentence, "token" : token, "img_path" : img_path} \
                ]}

    def gen_group_image(self, token, tree, depth):
        e = Digraph(self.argv.tetre_word, format=self.file_extension)
        e.attr('node', shape='box')

        current_id = self.current_token_id
        e.node(str(current_id), token.pos_)

        self.group_to_graph_recursive_with_depth(token, current_id, e, depth)

        img_name = 'command-group-'+self.argv.tetre_word+"-"+str(self.current_group_id)
        e.render(self.output_path + 'images/' + img_name)
        self.current_group_id += 1
        return 'images/' + img_name + "." + self.file_extension

    def group_to_graph_recursive_with_depth(self, token, parent_id, e, depth):
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
            self.group_to_graph_recursive_with_depth(child, child_id, e, depth-1)

        return

    def get_average_per_group(self):
        return int(self.get_sentence_totals() / len(self.groups))

    def get_max_params(self):
        max_params = 0

        for group in self.groups.values():
            if (group["params"] > max_params):
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
        max_sentences = 0

        # pprint.pprint(group_sorting(self.groups))

        for group in group_sorting(self.groups):

            t = Template(each_img_accumulator)
            c = Context({   "accumulator_img": group["img"], \
                            "total_group_sentences" : len(group["sentences"])})
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
        c = Context({"sentences_num" : len(self.sentence),
                     "groups_num": len(self.groups),
                     "max_group_num" : max_sentences,
                     "average_per_group" : avg_per_group,
                     "all_sentences": mark_safe(all_imgs_html),
                     "max_num_params": max_num_params,
                     "word": self.argv.tetre_word})

        with open(self.output_path + self.file_name, 'w') as output:
            output.write(t.render(c))

        return



class CommandSimplifiedGroup(CommandGroup):
    def __init__(self, argv):
        CommandGroup.__init__(self, argv)

    def run(self):
        rule_applier = Process()
        rule_applier_children = ProcessChildren()
        rule_extraction = ProcessExtraction()

        for token_original, sentence in get_tokens(self.argv):

            # print("------------------------------------------------------------------")
            # print()
            # print()
            # print(sentence)

            img_path = self.process_sentence(sentence)
            token = copy.deepcopy(token_original)
            tree = self.get_node_representation(token)

            tree, applied_verb = rule_applier.applyAll(tree, token)

            # print([tree, applied_verb])

            tree_grouping       = tree
            tree_subj_grouping  = ""
            tree_obj_grouping   = ""

            if self.argv.tetre_behaviour_root != "verb":
                tree_grouping = ""
                for child in token.children:
                    if self.argv.tetre_behaviour_root in child.dep_:
                        tree_grouping = self.get_node_representation(child)
                    if "subj" in child.dep_:
                        tree_subj_grouping = self.get_node_representation(child)
                    if "obj" in child.dep_:
                        tree_obj_grouping = self.get_node_representation(child)

            tree_obj_grouping, tree_subj_grouping, applied_obj_subj = rule_applier_children.applyAll(tree_obj_grouping, tree_subj_grouping, token)

            if ("subj" in self.argv.tetre_behaviour_root):
                tree_grouping = tree_subj_grouping
            if ("obj" in self.argv.tetre_behaviour_root):
                tree_grouping = tree_obj_grouping

            rules = rule_extraction.applyAll(tree, token, sentence)

            # print()
            # print()

            applied = applied_verb + applied_obj_subj

            self.group_accounting_add(tree_grouping, token, sentence, img_path, rules, applied)

        self.main_image = self.graph_gen_generate(self.accumulated_parents, self.accumulated_children)

        self.groups = self.filter(self.groups)

        if self.argv.tetre_output == "json":
            self.graph_gen_json()
        elif self.argv.tetre_output == "html":
            self.graph_gen_html()

    def gen_group_image(self, token, tree, depth):
        e = Digraph(self.argv.tetre_word, format=self.file_extension)
        e.attr('node', shape='box')

        current_id = self.current_token_id

        try:
            label = tree.label()
        except AttributeError:
            label = str(tree)

        e.node(str(current_id), label)

        current_global_id = {}

        if hasattr(tree, '__iter__'):
            for child in tree:
                self.current_token_id = self.current_token_id + 1
                current_global_id[str(self.current_token_id)] = child

            for child_id, child in current_global_id.items():
                e.node(child_id, "???")
                e.edge(str(current_id), child_id, label=child)

        img_name = 'command-simplified-group-'+self.argv.tetre_word+"-"+str(self.current_group_id)
        e.render(self.output_path + 'images/' + img_name)
        self.current_group_id += 1

        return 'images/' + img_name + "." + self.file_extension

    def group_accounting_add(self, tree, token, sentence, img_path, rules, applied):
        found = False

        string = nltk_tree_to_qtree(tree)
        # string2 = treenode_to_qtree(token)

        if (string in self.groups):
            group = self.groups[string]

            # group["sum"] = group["sum"] + 1
            group["sentences"].append({ \
                "sentence" : sentence, \
                "token" : token, \
                "img_path" : img_path, \
                "rules" : rules, \
                "applied" : applied
            })

        else:

            img = ""
            if self.argv.tetre_output == "html":
                img = self.gen_group_image(token, tree, self.depth)

            self.groups[string] = {"representative" : tree, \
                # "sum" : 1, \
                "params" : len(tree), \
                "img" : img, \
                "sentences" : [ \
                    {"sentence" : sentence, "token" : token, "img_path" : img_path, "rules" : rules, "applied" : applied} \
                ]}

    def get_results(self, sentence, to = False):
        rule = Reduction()

        has_subj    = False
        has_obj     = False

        subj        = ""
        obj         = ""
        others_html = ""
        others_json = []

        for results in sentence["rules"]:
            for key, values in results.items():
                dep = rule.rewrite_dp_tag(key)

                for value in values:
                    if dep == 'subj' and not has_subj:
                        subj = value
                        has_subj = True
                    elif dep == 'obj' and not has_obj:
                        obj = value
                        has_obj = True
                    else:
                        if self.argv.tetre_output == "json":
                            others_json.append({"relation": dep, "target": value})
                        elif self.argv.tetre_output == "html":
                            c = Context({"opt": dep, "result": value})
                            others_html += to.render(c)

        if self.argv.tetre_output == "json":
            return subj, obj, others_json
        elif self.argv.tetre_output == "html":
            return subj, obj, others_html

    def get_external_results(self, sentence):
        filename = self.argv.tetre_word+"-"+str(sentence["sentence"].file_id) \
                    +"-"+str(sentence["sentence"].id)+"-"+str(sentence["token"].idx)

        allenai_openie  = dirs['output_allenai_openie']['path'] + filename
        stanford_openie = dirs['output_stanford_openie']['path'] + filename
        mpi_clauseie    = dirs['output_mpi_clauseie']['path'] + filename

        text_allenai_openie  = ""
        text_stanford_openie = ""
        text_mpi_clauseie    = ""

        try:
            with open(allenai_openie, 'r') as text_allenai_openie:
                text_allenai_openie = text_allenai_openie.read()
        except:
            pass

        try:
            with open(stanford_openie, 'r') as text_stanford_openie:
                text_stanford_openie = text_stanford_openie.read()
        except:
            pass

        try:
            with open(mpi_clauseie, 'r') as text_mpi_clauseie:
                text_mpi_clauseie = text_mpi_clauseie.read()
        except:
            pass

        return  text_allenai_openie.replace('\n', '<br />'), \
                text_stanford_openie.replace('\n', '<br />'), \
                text_mpi_clauseie.replace('\n', '<br />')

    def graph_gen_html_sentence(self, sentence, i):
        each_sentence = ""
        each_sentence_opt = ""

        with open(html_templates + 'each_sentence.html', 'r') as each_sentence:
            each_sentence = each_sentence.read()

        with open(html_templates + 'each_sentence_opt.html', 'r') as each_sentence_opt:
            each_sentence_opt = each_sentence_opt.read()

        to = Template(each_sentence_opt)
        
        subj, obj, others = self.get_results(sentence, to)

        text_allenai_openie = text_stanford_openie = text_mpi_clauseie = ""

        if self.argv.tetre_include_external:
            text_allenai_openie, text_stanford_openie, text_mpi_clauseie = self.get_external_results(sentence)

        ts = Template(each_sentence)
        c = Context({
                     "add_external": self.argv.tetre_include_external,
                     "gf_id": sentence["sentence"].file_id,
                     "gs_id": sentence["sentence"].id,
                     "gt_id": sentence["token"].idx,
                     "path": sentence["img_path"],
                     "sentence": mark_safe(highlight_word(sentence["sentence"], self.argv.tetre_word)),
                     "subj" : subj,
                     "obj" : obj,
                     "rel" : self.argv.tetre_word,
                     "others" : mark_safe(others),
                     "rules_applied" : mark_safe(", ".join(sentence["applied"])),
                     "text_allenai_openie" : mark_safe(highlight_word(text_allenai_openie, self.argv.tetre_word)),
                     "text_stanford_openie" : mark_safe(highlight_word(text_stanford_openie, self.argv.tetre_word)),
                     "text_mpi_clauseie" : mark_safe(highlight_word(text_mpi_clauseie, self.argv.tetre_word))
                })

        return ts.render(c)


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

        with open(html_templates + 'each_img_accumulator.html', 'r') as each_img_accumulator:
            each_img_accumulator = each_img_accumulator.read()

        i = 0

        all_imgs_html = ""
        max_sentences = 0

        # pprint.pprint(group_sorting(self.groups))
        
        for group in group_sorting(self.groups):
            # group = self.groups[key]

            t = Template(each_img_accumulator)
            c = Context({   "accumulator_img": group["img"], \
                            "total_group_sentences" : len(group["sentences"])})
            all_imgs_html += t.render(c)

            each_sentence_html = ""

            if len(group["sentences"]) > max_sentences:
                max_sentences = len(group["sentences"])

            for sentence in group["sentences"]:

                if (self.argv.tetre_output_csv):
                    csv_row = [self.argv.tetre_word,
                    str(sentence["sentence"].file_id)+"-"+str(sentence["sentence"].id)+"-"+str(sentence["token"].idx)]

                    wr = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
                    wr.writerow(csv_row)

                each_sentence_html += self.graph_gen_html_sentence(sentence, i)
                i += 1

            all_imgs_html += each_sentence_html

        avg_per_group = self.get_average_per_group()
        max_num_params = self.get_max_params()

        t = Template(index_group)
        c = Context({"sentences_num" : self.get_sentence_totals(),
                     "groups_num": len(self.groups),
                     "max_group_num" : max_sentences,
                     "average_per_group" : avg_per_group,
                     "all_sentences": mark_safe(all_imgs_html),
                     "max_num_params": max_num_params,
                     "word": self.argv.tetre_word})

        with open(self.output_path + self.file_name, 'w') as output:
            output.write(t.render(c))

        return

    def graph_gen_json(self):
        json_result = []

        for group in group_sorting(self.groups):
            for sentence in group["sentences"]:
                subj, obj, others = self.get_results(sentence)

                json_result.append(
                    {"sentence": str(sentence["sentence"]),
                     "relation" : {"rel": self.argv.tetre_word, "subj" : subj, "obj" : obj},
                     "other_relations" : others,
                     "rules_applied" : ",".join(sentence["applied"])})

        print(json.dumps(json_result, sort_keys=True))

    def filter(self, groups):

        if (self.argv.tetre_sampling == None):
            return groups

        sampling = float(self.argv.tetre_sampling)
        seed = int(self.argv.tetre_seed)

        simplified_groups = {}

        random.seed(seed)

        for key, group in self.groups.items():

            qty = int(self.percentage(sampling, len(group["sentences"])))

            if qty < 1:
                qty = 1

            simplified_groups[key] = {}
            for inner_key, inner_values in group.items():
                simplified_groups[key][inner_key] = inner_values
            
            simplified_groups[key].pop('sentences', None)
            simplified_groups[key]["sentences"] = []

            for i in range(0, qty):
                simplified_groups[key]["sentences"].append(
                    group["sentences"][i]
                )
        
        return simplified_groups