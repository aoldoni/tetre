from openie import *
from directories import *

from tetre.graph import *
from tetre.dependency_helpers import *
from tetre.possible_relations import *


def argv_preprocessing(argv):
    if argv.tetre_output == "html_csv":
        argv.tetre_output = "html"
        argv.tetre_output_csv = True

    return argv


def run(argv):

    argv = argv_preprocessing(argv)

    if (argv.tetre_behaviour == "accumulator"):
        cmd = CommandAccumulative(argv)
    elif (argv.tetre_behaviour == "groupby"):
        cmd = CommandGroup(argv)
    elif (argv.tetre_behaviour == "simplified_groupby"):
        cmd = CommandSimplifiedGroup(argv)
    else:
        print("No command!")
        return

    cmd.run()