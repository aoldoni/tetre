

def start(argv):
    """Module entry point for the command line.

    Args:
        argv: The command line parameters.

    """
    if argv.workflow == "stats":
        import postprocess.stats as stats
        stats.run(argv)

    else:
        print("Not implemented.")
