#!/usr/bin/env python

import sys
import os
from internallib.directories import *

def recompile_stanford():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    os.chdir(script_dir + "/" + stanford_path)
    os.system("ant clean")
    os.system("ant")
    os.system("rm stanford-corenlp-dblp.jar")
    os.system("cd classes ; jar -cfm ../stanford-corenlp-dblp.jar ../src/META-INF/MANIFEST.MF edu ; cd ..")
    os.chdir(script_dir)

def regenerate(argv):
    print "Recompile Stanford CoreNLP..."
    recompile_stanford()


if __name__ == '__main__':
    sys.exit(regenerate(sys.argv))
