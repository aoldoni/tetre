

def start(argv):
    """Module entry point for the command line.

    Args:
        argv: The command line parameters.

    """
    if argv.workflow == 'brat_to_stanford':
        import brat_to_stanford.train as train
        train.regenerate(argv)

    if argv.workflow != 'brat_to_stanford':
        print("Not implemented.")
