from graphviz import Digraph

import json
import copy
import random
import csv

import django
from django.utils.safestring import mark_safe
from django.template import Template, Context
from django.conf import settings

from tree_utils import *

from directories import dirs

from tetre.graph_group import CommandGroup
from tetre.graph_processing import Process, Reduction
from tetre.graph_processing_children import ProcessChildren
from tetre.graph_extraction import ProcessExtraction
from tetre.dependency_helpers import *


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

        img_name = 'command-simplified-group-'+ self.argv.tetre_word + "-" + str(self.current_group_id)
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
                "sentence": sentence, \
                "token": token, \
                "img_path": img_path, \
                "rules": rules, \
                "applied": applied
            })

        else:

            img = ""
            if self.argv.tetre_output == "html":
                img = self.gen_group_image(token, tree, self.depth)

            self.groups[string] = {"representative": tree, \
                                   # "sum" : 1, \
                                   "params": len(tree), \
                                   "img": img, \
                                   "sentences": [ \
                                       {"sentence": sentence, "token": token, "img_path": img_path, "rules": rules,
                                        "applied": applied} \
                                       ]}

    def get_results(self, sentence, to=False):
        rule = Reduction()

        has_subj = False
        has_obj = False

        subj = ""
        obj = ""
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
        filename = self.argv.tetre_word + "-" + str(sentence["sentence"].file_id) \
                   + "-" + str(sentence["sentence"].id) + "-" + str(sentence["token"].idx)

        allenai_openie = dirs['output_allenai_openie']['path'] + filename
        stanford_openie = dirs['output_stanford_openie']['path'] + filename
        mpi_clauseie = dirs['output_mpi_clauseie']['path'] + filename

        text_allenai_openie = ""
        text_stanford_openie = ""
        text_mpi_clauseie = ""

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

        return text_allenai_openie.replace('\n', '<br />'), \
               text_stanford_openie.replace('\n', '<br />'), \
               text_mpi_clauseie.replace('\n', '<br />')

    def graph_gen_html_sentence(self, sentence, i):
        each_sentence = ""
        each_sentence_opt = ""

        with open(dirs['html_templates']['path'] + 'each_sentence.html', 'r') as each_sentence:
            each_sentence = each_sentence.read()

        with open(dirs['html_templates']['path'] + 'each_sentence_opt.html', 'r') as each_sentence_opt:
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
            "subj": subj,
            "obj": obj,
            "rel": self.argv.tetre_word,
            "others": mark_safe(others),
            "rules_applied": mark_safe(", ".join(sentence["applied"])),
            "text_allenai_openie": mark_safe(highlight_word(text_allenai_openie, self.argv.tetre_word)),
            "text_stanford_openie": mark_safe(highlight_word(text_stanford_openie, self.argv.tetre_word)),
            "text_mpi_clauseie": mark_safe(highlight_word(text_mpi_clauseie, self.argv.tetre_word))
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

        with open(dirs['html_templates']['path'] + 'index_group.html', 'r') as index_group:
            index_group = index_group.read()

        with open(dirs['html_templates']['path'] + 'each_img_accumulator.html', 'r') as each_img_accumulator:
            each_img_accumulator = each_img_accumulator.read()

        i = 0

        all_imgs_html = ""
        max_sentences = 0

        # pprint.pprint(group_sorting(self.groups))

        for group in group_sorting(self.groups):
            # group = self.groups[key]

            t = Template(each_img_accumulator)
            c = Context({"accumulator_img": group["img"], \
                         "total_group_sentences": len(group["sentences"])})
            all_imgs_html += t.render(c)

            each_sentence_html = ""

            if len(group["sentences"]) > max_sentences:
                max_sentences = len(group["sentences"])

            for sentence in group["sentences"]:

                if (self.argv.tetre_output_csv):
                    csv_row = [self.argv.tetre_word,
                               str(sentence["sentence"].file_id) + "-" + str(sentence["sentence"].id) + "-" + str(
                                   sentence["token"].idx)]

                    wr = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
                    wr.writerow(csv_row)

                each_sentence_html += self.graph_gen_html_sentence(sentence, i)
                i += 1

            all_imgs_html += each_sentence_html

        avg_per_group = self.get_average_per_group()
        max_num_params = self.get_max_params()

        t = Template(index_group)
        c = Context({"sentences_num": self.get_sentence_totals(),
                     "groups_num": len(self.groups),
                     "max_group_num": max_sentences,
                     "average_per_group": avg_per_group,
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
                     "relation": {"rel": self.argv.tetre_word, "subj": subj, "obj": obj},
                     "other_relations": others,
                     "rules_applied": ",".join(sentence["applied"])})

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