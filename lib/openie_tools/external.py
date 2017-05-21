import os

from tetre.dependency_helpers import get_tokens
from openie_tools.interfaces import ExternalInterface
from directories import dirs, should_skip_file


class ExternalToolsPrepare:
    """Obtains the segments from the sentences, but only the sentences containing the token being searched for.
    Each sentence for the occurrence of the token is then saved in a separate file.
    Each file will then later serve as an input for the external tools.
    The file is named with a unique combination of the word and the positions in the files, sentences and token.

    Note that this forces the external tool to use the sentences without context, as segmented by SpaCy.
    """
    def __init__(self, args):
        self.args = args

    def run(self):
        output_path = dirs['output_comparison']['path']

        for token_original, sentence in get_tokens(self.args):
            filename = self.args.tetre_word+"-"+str(sentence.file_id)+"-"+str(sentence.id)+"-"+str(token_original.idx)

            with open(output_path + filename, 'w') as output:
                output.write(str(sentence))

        return


class ExternalToolsRun:
    """Lists all files from the preparation directory and then run the selected external tool on the file.
    Each file contains one sentence.
    """
    def __init__(self, args):
        self.args = args

    def run(self):
        # prepares the default external interface
        interface = ExternalInterface(self.args)

        # obtain files from the prepepared path
        lst = os.listdir(dirs['output_comparison']['path'])

        # file list is sorted so results list are stable
        lst.sort()

        for fn in lst:
            if should_skip_file(fn):
                continue

            if self.args.tetre_word not in fn:
                continue

            file = dirs['output_comparison']['path'] + fn
            out = interface.get_interface().output_dir + fn
            interface.run(file, out)
