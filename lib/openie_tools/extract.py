from openie import *
from directories import *
from dependency_helpers import *
from graph import *
from possible_relations import *


def run(argv):
    if (argv.tetre_prepare_sentences):
        cmd = ExternalToolsPrepare(argv)
        cmd.run()
    elif (argv.tetre_run_others):
        cmd = ExternalToolsRun(argv)
        cmd.run()
    elif (argv.tetre_stats):
        cmd = PossibleRelations(argv)
        cmd.run()
    else:
        print("No command!")