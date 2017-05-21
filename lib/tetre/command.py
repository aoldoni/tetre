from parsers_cache import get_cached_sentence_image
from directories import dirs
from tree_utils import nltk_tree_to_qtree

from graphviz import Digraph

file_extension = "png"


class ResultsGroupMatcher(object):
    def __init__(self, argv):
        self.argv = argv

        self.groups = {}
        self.current_group_id = 0

    def get_groups(self):
        return self.groups

    def set_groups(self, groups):
        self.groups = groups

    def group_accounting_add(self, tree, token, sentence, img_path, representative, img_renderer, rules=(), applied=()):
        string = nltk_tree_to_qtree(tree)

        if string in self.groups:
            group = self.groups[string]

            group["sentences"].append({
                "sentence": sentence,
                "token": token,
                "img_path": img_path,
                "rules": rules,
                "applied": applied
            })

        else:
            img = ""

            if self.argv.tetre_output == "html":
                img = img_renderer.gen_group_image(representative)

            self.groups[string] = {"representative": tree,
                                   "params": len(tree),
                                   "img": img,
                                   "sentences": [
                                       {"sentence": sentence,
                                        "token": token,
                                        "img_path": img_path,
                                        "rules": rules,
                                        "applied": applied}
                                       ]}

    def get_max_params(self):
        max_params = 0

        for group in self.groups.values():
            if group["params"] > max_params:
                max_params = group["params"]

        return max_params

    def get_average_per_group(self):
        return int(self.get_sentence_totals() / len(self.groups))

    def get_sentence_totals(self):
        total = 0

        for key, group in self.groups.items():
            total += len(group["sentences"])

        return total


class SentencesAccumulator(object):
    def __init__(self, argv):
        self.argv = argv

        self.sentence_imgs = []
        self.sentence = []

        self.current_token_id = 0
        self.current_sentence_id = 0

    def process_sentence(self, sentence):
        self.sentence.append(str(sentence).replace("\r", "").replace("\n", "").strip())
        if self.argv.tetre_output == "html":
            return self.sentence_to_graph(sentence)
        else:
            return ""

    def sentence_to_graph(self, sentence):
        img_name = 'sentence-' + str(sentence.file_id) + "-" + str(sentence.id)
        img_dot_path = 'images/' + img_name
        img_path = img_dot_path + "." + file_extension
        self.sentence_imgs.append(img_path)

        found = get_cached_sentence_image(self.argv,
                                          dirs['output_html']['path'],
                                          sentence,
                                          file_extension)

        if not found:
            e = Digraph(self.argv.tetre_word, format=file_extension)
            e.attr('node', shape='box')
            e.attr('graph', label=str(sentence))

            current_id = self.current_token_id
            self.sentence_to_graph_add_node(e, current_id, sentence.root.orth_)
            self.sentence_to_graph_recursive(sentence.root, current_id, e)
            e.render(dirs['output_html']['path'] + img_dot_path)

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

    def sentence_to_graph_add_node(self, e, current_id, orth_):
        if orth_ == self.argv.tetre_word:
            e.node(str(current_id), orth_, fillcolor="dimgrey", fontcolor="white", style="filled")
        else:
            e.node(str(current_id), orth_)
