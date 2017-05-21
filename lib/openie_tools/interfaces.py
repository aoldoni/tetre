from directories import dirs
import os


class StanfordOpenIE:
    def __init__(self, argv):
        """Initializes default interface parameters and stores command line parameters internally.

        Args:
            argv: An object with the command line arguments.

        """
        self.argv = argv
        self.output_dir = dirs['output_stanford_openie']['path']

    @staticmethod
    def run(i, o):
        """Runs the Stanford Open Information Extractor tool on the file containing the segmented sentence.

        Args:
            i: Input file.
            o: Output file containing the results (extracted relations) from the external tool.

        """
        command = ''.join(['java -cp ', dirs['stanford_corenlp_path']['path'],
                           '*:', dirs['stanford_corenlp_path']['path'], 'lib/* ',
                           '-Xmx8g edu.stanford.nlp.naturalli.OpenIE -props ',
                           dirs['config']['path'], 'pipeline-openie.properties ', i, ' 1>', o])

        os.system(command)


class AllenAIOpenIE:
    def __init__(self, argv):
        """Initializes default interface parameters and stores command line parameters internally.

        Args:
            argv: An object with the command line arguments.

        """
        self.argv = argv
        self.output_dir = dirs['output_allenai_openie']['path']

    @staticmethod
    def run(i, o):
        """Runs the AllenAI Open Information Extractor tool on the file containing the segmented sentence.

        Args:
            i: Input file.
            o: Output file containing the results (extracted relations) from the external tool.

        """
        command = ''.join(['(cd ', dirs['allenai_root']['path'],
                           '; ', 'sbt \'run-main edu.knowitall.openie.OpenIECli --input-file ',
                           dirs['allenai_root']['root_distance'], i, ' --ouput-file ',
                           dirs['allenai_root']['root_distance'], o, '\')'])

        os.system(command)


class MPICluaseIE:
    def __init__(self, argv):
        """Initializes default interface parameters and stores command line parameters internally.

        Args:
            argv: An object with the command line arguments.

        """
        self.argv = argv
        self.output_dir = dirs['output_mpi_clauseie']['path']

    @staticmethod
    def run(i, o):
        """Runs the Max Planck Institute Open Information Extractor tool on the file containing the segmented sentence.

        Args:
            i: Input file.
            o: Output file containing the results (extracted relations) from the external tool.

        """
        command = ''.join(['./', dirs['clauseie_root']['path'], 'clausie.sh -f ', i, ' -o ', o])

        os.system(command)


class ExternalInterface:
    def __init__(self, argv):
        """Initializes default interface parameters and stores command line parameters internally.

        Args:
            argv: An object with the command line arguments.

        """
        self.argv = argv
        self.classes = ["MPICluaseIE", "AllenAIOpenIE", "StanfordOpenIE"]
        self.interface = None

    def run(self, file, outfile):
        """Runs the selected tool on the file containing the segmented sentence.

        Args:
            file: Input file.
            outfile: Output file containing the results (extracted relations) from the external tool.

        """
        external = self.get_interface()
        external.run(file, outfile)

        return

    def get_interface(self):
        """Returns the class instance for the interface with the selected external tool.
        """

        class_name = self.argv.openie_run_others

        if class_name in self.classes:
            self.interface = globals()[class_name](self.argv)

        return self.interface
