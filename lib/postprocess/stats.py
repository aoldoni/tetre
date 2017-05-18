from tetre.dependency_helpers import get_uncached_tokens


class PossibleRelations(object):
    def __init__(self, argv):
        """Constructor, simply stores command line parameters internally.

         Args:
             argv: An object with the command line arguments.

         """
        self.argv = argv

    def run(self):
        """Search more popular verbs (VBZ, VERB, VerbForm=fin Tense=pres Number=sing Person=3).
         """

        struct = {}

        for token, sentence in get_uncached_tokens(self.argv):
            if token.tag_ == "VBZ":
                if token.orth_ not in struct:
                    struct[token.orth_] = 1
                else:
                    struct[token.orth_] += 1

        # sort keys by value
        sorted_struct = sorted(struct.items(), key=lambda x: x[1], reverse=True)

        # structure the output text: word,N
        prepared_output = "\n".join([str(word[0]) + "," + str(word[1]) for word in sorted_struct])

        print(prepared_output)


def run(argv):
    """Module entry point for the command line.

    Args:
        argv: The command line parameters.

    """
    cmd = PossibleRelations()
    cmd.run
