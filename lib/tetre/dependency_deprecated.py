def spacy_tree_noun_detection(skip_token, token, all_noun_chuncks, initial_direction=-1):
    dep_labels = []

    direction = initial_direction
    inverse_direction = direction * -1

    # first try to go in one direction
    if (direction == -1):
        children_list = list(token.children)

        # print("\t", ["DEBUG", token, token.dep_, [[i, i.dep_] for i in children_list], direction])

        for i in range(0, len(children_list)):
            child = list(token.children)[i]

            if (child is not token and \
                child is not skip_token and \
                child.pos_ == 'NOUN'):
                for nc in all_noun_chuncks:
                    if (child in list(nc)):
                        dep_labels.append(nc)
                        return dep_labels

            if (len(list(child.children)) > 0):
                return spacy_tree_noun_detection(token, child, all_noun_chuncks, direction)

    if (direction == 1):

        # print("\t", ["DEBUG", token, token.dep_, token.head, token.head.dep_, direction])

        if (token.head is not token and \
            token.head is not skip_token and \
            token.head.pos_ == 'NOUN'):

            for nc in all_noun_chuncks:
                if (token.head in list(nc)):
                    dep_labels.append(nc)
                    return dep_labels

        if (token.head is token):
            return spacy_tree_noun_detection(token, token.head, all_noun_chuncks, inverse_direction)
        elif token.head is not token:
            return spacy_tree_noun_detection(token, token.head, all_noun_chuncks, direction)

    return dep_labels

def spacy_dependency_labels_to_leaf(token):
    '''Walk up the syntactic tree, collecting the arc labels.'''
    dep_labels = []
    for child in token.subtree:
        if (child is not token):
            dep_labels.append(child)

    return dep_labels

def spacy_dependency_labels_to_root(token):
    '''Walk up the syntactic tree, collecting the arc labels.'''
    dep_labels = []
    while token.head is not token:
        dep_labels.append(token.head)
        token = token.head
    return dep_labels