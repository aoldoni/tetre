

def start(argv):
    """Module entry point for the command line.

    Args:
        argv: The command line parameters.

    """
    if ap.workflow == 'brat_to_stanford':
        import brat_to_stanford.compile as compile
        compile.regenerate(argv)

    if ap.workflow != 'brat_to_stanford':
        print("Not implemented.")
