def pattern_based_finder_dobj_right(token, all_noun_chuncks):
    nc = None

    where_to_dobj_from = token

    for child in where_to_dobj_from.children:
        if (child.dep_ == "dobj"):
            final_token = patter_recurse_on_prep(child)

            nc = get_noun_chunck(final_token, all_noun_chuncks)

    return nc

def patter_recurse_on_prep(token):

    where_to_dobj_from = token
    
    prep_found = False
    for child in token.children:
        # print(["1", token, child, child.dep_, child.orth_ ])
        if (child.dep_ == "prep" and child.orth_ == "of"):
            prep_found = True
            where_to_dobj_from = child

    # print(["2", prep_found])

    if not prep_found:
        return token
    else:
        for grangrandchild in where_to_dobj_from.children:
            # print(["3", token, where_to_dobj_from, grangrandchild, grangrandchild.pos_])
            if (grangrandchild.pos_ == "NOUN"):
                return patter_recurse_on_prep(grangrandchild)

def get_noun_chunck(token, all_noun_chuncks):
    for nc in all_noun_chuncks:
        if (token in list(nc)):
            return nc

def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.dep_+"/"+node.orth_+"/"+node.pos_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.dep_+"/"+node.orth_+"/"+node.pos_

def print_tree(sent):
    to_nltk_tree(sent.root).pretty_print()