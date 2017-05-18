from tetre.command_accumulative import CommandAccumulative
from tetre.command_group import CommandGroup
from tetre.command_simplified import CommandSimplifiedGroup


def argv_preprocessing(argv):
    if argv.tetre_output == "html_csv":
        argv.tetre_output = "html"
        argv.tetre_output_csv = True

    behaviours_needs_word = ["accumulator", "groupby", "simplified_groupby"]
    if any(argv.tetre_behaviour in b for b in behaviours_needs_word) and not isinstance(argv.tetre_word, str):
        print("Please define --tetre_word param")

    return argv


def run(argv):
    argv = argv_preprocessing(argv)

    if argv.tetre_behaviour == "accumulator":
        cmd = CommandAccumulative(argv)
    elif argv.tetre_behaviour == "groupby":
        cmd = CommandGroup(argv)
    elif argv.tetre_behaviour == "simplified_groupby":
        cmd = CommandSimplifiedGroup(argv)
    else:
        print("No command!")
        return

    cmd.run()
