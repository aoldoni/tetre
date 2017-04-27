from tetre.dependency_helpers import get_uncached_tokens

class PossibleRelations(object):
    def __init__(self, args):
        self.args = args

    def run(self):

        struct = {}

        for token, sentence in get_uncached_tokens(self.args):
            if (token.tag_ == "VBZ"):
                if (token.orth_ not in struct):
                    struct[token.orth_] = 1
                else:
                    struct[token.orth_] += 1

        sorted_struct = sorted(struct.items(), key=lambda x: x[1], reverse=True)

        print("\n".join([str(word[0]) + "," + str(word[1]) for word in sorted_struct]))
