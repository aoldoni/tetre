import os
from directories import dirs


def remove_dirs():
    """Not implemented yet. Should restore the local folder to the original state, e.g.: delete folder with data.
    """
    print("Not implemented.")
    return

    # Future possible implementation is something more robust than the below.

    # import shutil
    # for directory in directories.dirs.values():
    #     shutil.rmtree(directory)


def setup_dirs():
    """Generated all the folders needed for the initial operation of the tool.

    Generate all folders contained in the lib/directories.py file in case they don't exist.

    """
    for directory in dirs.values():
        current_path = directory['path']

        if not os.path.exists(current_path):
            os.makedirs(current_path)


def start(argv):
    """Module entry point for the command line.

    Args:
        argv: The command line parameters.

    """
    if argv.reset:
        remove_dirs()
    else:
        setup_dirs()