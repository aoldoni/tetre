from openie_tools.external import *


def run(argv):
    if (argv.openie_prepare_sentences):
        cmd = ExternalToolsPrepare(argv)
        cmd.run()
    elif (argv.openie_run_others):
        cmd = ExternalToolsRun(argv)
        cmd.run()
    else:
        print("No command!")