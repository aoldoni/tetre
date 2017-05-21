import os
from directories import dirs


def recompile_stanford(argv):
    """Recompiles stanford CoreNLP.

    Args:
        argv: An object with the command line arguments.

    """

    script_dir = argv.root_dir

    os.chdir(script_dir + "/" + dirs['stanford_corenlp_path']['path'])
    os.system("ant clean")
    os.system("ant")
    os.system("rm stanford-corenlp.jar stanford-corenlp-3.6.0.jar stanford-corenlp-compiled.jar")
    os.system("cd classes ; jar -cfm ../stanford-corenlp-compiled.jar ../src/META-INF/MANIFEST.MF edu ; cd ..")

    print("File stanford-corenlp-compiled.jar generated...")
    os.chdir(script_dir)


def regenerate(argv):
    """Recompiles stanford CoreNLP (entry point from the command line).

    Args:
        argv: An object with the command line arguments.

    """
    print("Recompile Stanford CoreNLP...")
    recompile_stanford(argv)
