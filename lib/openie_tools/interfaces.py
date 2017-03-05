from directories import *
from pydoc import locate

import os

class StanfordOpenIE():
    def __init__(self, args):
        self.args = args
        self.dir = output_stanford_openie

    def run(self, i, o):
        os.system('java -cp stanford/stanford-corenlp-full-2015-12-09/*:stanford/stanford-ner-2015-12-09/lib/* -Xmx8g edu.stanford.nlp.naturalli.OpenIE -props '+config+'pipeline-openie.properties ' + i + ' 1>' + o)

class AllenAIOpenIE():
    def __init__(self, args):
        self.args = args
        self.dir = output_allenai_openie

    def run(self, i, o):
        os.system('(cd allenai_openie/; sbt \'run-main edu.knowitall.openie.OpenIECli --input-file ../'+i+' --ouput-file ../'+o+'\')')

class MPICluaseIE():
    def __init__(self, args):
        self.args = args
        self.dir = output_mpi_clauseie

    def run(self, i, o):
        os.system('./clausie/clausie.sh -f '+i+' -o '+o+'')

class ExternalInterface():
    def __init__(self, args):
        self.args = args
        self.classes = ["MPICluaseIE", "AllenAIOpenIE", "StanfordOpenIE"]
        self.interface = None

    def run(self, file, outfile):
        external = self.get_interface()
        external.run(file, outfile)

        return

    def get_interface(self):

        if self.args.run_with_others in self.classes:
            for the_class in globals():
                self.interface = globals()[self.args.run_with_others](self.args)

        return self.interface

