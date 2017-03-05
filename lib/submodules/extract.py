

def start(argv):
    """Module entry point for the command line.

    Args:
        argv: The command line parameters.

    """
    if argv.workflow == 'brat_to_stanford':
        import brat_to_stanford.extract as extract
        extract.run(argv)

    elif argv.workflow == 'tetre':
        import tetre.extract as extract
        extract.run(argv)

    else:
        print("Not implemented.")
