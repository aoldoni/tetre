

def start(argv):
    """Module entry point for the command line.

    Args:
        argv: The command line parameters.

    """
    if argv.workflow == 'microsoft_gazette':
        import microsoft_gazette.process as process
        process.run(argv)

    else:
        print("Not implemented.")
