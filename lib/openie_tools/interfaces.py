from directories import dirs

import os


class StanfordOpenIE():
    def __init__(self, args):
        self.args = args
        self.output_dir = dirs['output_stanford_openie']['path']

    @staticmethod
    def run(i, o):
        command = ''.join(['java -cp ', dirs['stanford_corenlp_path']['path'],
                           '*:', dirs['stanford_corenlp_path']['path'], 'lib/* ',
                           '-Xmx8g edu.stanford.nlp.naturalli.OpenIE -props ',
                           dirs['config']['path'], 'pipeline-openie.properties ', i, ' 1>', o])

        os.system(command)


class AllenAIOpenIE():
    def __init__(self, args):
        self.args = args
        self.output_dir = dirs['output_allenai_openie']['path']

    @staticmethod
    def run(i, o):
        command = ''.join(['(cd ', dirs['allenai_root']['path'],
                           '; ', 'sbt \'run-main edu.knowitall.openie.OpenIECli --input-file ',
                           dirs['allenai_root']['root_distance'], i, ' --ouput-file ',
                           dirs['allenai_root']['root_distance'], o, '\')'])

        os.system(command)


class MPICluaseIE():
    def __init__(self, args):
        self.args = args
        self.output_dir = dirs['output_mpi_clauseie']['path']

    @staticmethod
    def run(i, o):
        command = ''.join(['./',
                           dirs['clauseie_root']['path'],
                           'clausie.sh -f ', i, ' -o ', o])

        os.system(command)


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

        class_name = self.args.openie_run_others

        if class_name in self.classes:
            self.interface = globals()[class_name](self.args)

        return self.interface
