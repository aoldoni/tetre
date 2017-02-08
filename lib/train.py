

def start(ap):
    """Module entry point for the command line.

    Args:
        ap (:obj:`ArgumentParser`): The command line parameters.

    """
    if ap.workflow == 'brat_to_stanford':
        import training.brat_to_stanford as brat_to_stanford
        brat_to_stanford.regenerate(ap)

    if ap.workflow != 'brat_to_stanford':
        print("Not implemented.")
