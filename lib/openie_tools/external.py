from tetre.dependency_helpers import get_tokens
from openie_tools.interfaces import ExternalInterface
from directories import dirs
import os

class ExternalToolsPrepare():
    def __init__(self, args):
        self.args = args

    def run(self):
        for token_original, sentence in get_tokens(self.args):
            filename = self.args.tetre_word+"-"+str(sentence.file_id)+"-"+str(sentence.id)+"-"+str(token_original.idx)
            output_path = dirs['output_comparison']['path']

            with open(output_path + filename, 'w') as output:
                output.write(str(sentence))

        return

class ExternalToolsRun():
    def __init__(self, args):
        self.args = args

    def run(self):
        interface = ExternalInterface(self.args)

        lst = os.listdir(dirs['output_comparison']['path'])
        lst.sort()

        for fn in lst:

            if fn == ".DS_Store":
                continue

            if self.args.tetre_word not in fn:
                continue

            file = dirs['output_comparison']['path'] + fn
            out = interface.get_interface().output_dir + fn
            interface.run(file, out)
