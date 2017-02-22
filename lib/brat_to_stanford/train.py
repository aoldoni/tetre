import os

from logging import error

from standoff2other.postag import merge_pos
from standoff2other.standoff2conll import conversion_entry, OUTPUT_TYPES
from directories import dirs


def clean_data():
    """Deletes previously generated models and intermediate data.

    """
    os.system(''.join(['rm ', dirs['transformed']['path'], '*']))
    os.system(''.join(['rm ', dirs['models']['path'], '*.ser']))
    os.system(''.join(['rm ', dirs['models']['path'], '*.ser.gz']))


def transform_ner_from_standoff(file):
    """Entry point for data transformation.

    Entry point as to transform annotated Brat files (standoff format) to
    Stanford's NER training format.

    Args:
        file: A string with the directory to be transformed.

    """

    # alternative as library for the following command line
    # os.system('python standoff2others/standoff2conll.py annotated/ > training/dblp.tsv')
    with open(file, 'w') as output:
        data = conversion_entry([dirs['annotated']['path']], OUTPUT_TYPES[0])
        if data:
            output.write(data)
        else:
            error("No data could be written, please check if Brat input is in the correct folder.")


def transform_rel_from_standoff(file, filepos):
    """Entry point for data transformation.

    Entry point as to transform annotated Brat files (standoff format) to
    Stanford's Relation Extractor training format.

    Args:
        file: A string with the directory to be transformed.

    """
    # alternative as library for the following command line
    # os.system('python standoff2others/standoff2conll.py annotated/ > training/dblp.tsv')
    with open(file, 'w') as output:
        data = conversion_entry([dirs['annotated']['path']], OUTPUT_TYPES[1], filepos)
        if data:
            output.write(data)
        else:
            error("No data could be written, please check if Brat input is in the correct folder.")


def run_google(argv):
    """Adds POS-tagging to the text being transformed for training.

    Utilises Google's Parsey / Tensorflow model to add POS-tagging
    to the text at hand being transformed. This is necessary since
    the training of the models in the stanford NER requires POS-tag
    as part of the input.
    Google's Parsey / Tensorflow was chosen just for experimental purposes.

    Args:
        argv: An object with the command line arguments, expected to have
        a root_dir property, containing the root folder of the TETRE's
        folder structure.

    """

    script_dir = argv.root_dir
    root_dir_distance = dirs['google_parsey_path']['root_distance']

    # go into the dir of installation
    os.chdir(''.join([script_dir, '/', dirs['google_parsey_path']['path']]))

    print(''.join(['cat ', root_dir_distance, dirs['transformed']['path'],
                   "dblp.tsv | awk '{ print $1 }' | syntaxnet/google.sh 1>", root_dir_distance,
                   dirs['transformed']['path'], 'pos.tsv']))
    os.system(''.join(['cat ', root_dir_distance, dirs['transformed']['path'],
                       "dblp.tsv | awk '{ print $1 }' | syntaxnet/google.sh 1>", root_dir_distance,
                       dirs['transformed']['path'], 'pos.tsv']))

    # remove empty lines
    os.system(''.join(["awk 'NF' ", root_dir_distance, dirs['transformed']['path'],
                      'dblp.tsv > ', root_dir_distance, dirs['transformed']['path'], 'noempty.tsv']))
    os.system(''.join(["awk 'NF' ", root_dir_distance, dirs['transformed']['path'],
                      'pos.tsv > ', root_dir_distance, dirs['transformed']['path'], 'pos-noempty.tsv']))

    # back to the original directory
    os.chdir(script_dir)


def train_stanford_ner():
    """Trains the NER model using the Stanford CoreNLP.

    """

    os.system(''.join(['java -cp',
                       ' "' + dirs['stanford_ner_path']['path'] +
                       'stanford-ner.jar:' + dirs['stanford_ner_path']['path'] + 'lib/*"',
                       ' edu.stanford.nlp.ie.crf.CRFClassifier -prop ', dirs['config']['path']+'ner.properties']))


def train_stanford_rel():
    """Trains the Relation Extractor model using the Stanford CoreNLP.

    """

    os.system(''.join(['java -cp ' + dirs['stanford_corenlp_path']['path'] + '/*:' +
                       dirs['stanford_ner_path']['path'] + '/lib/*',
                       ' edu.stanford.nlp.ie.machinereading.MachineReading --arguments ',
                       dirs['config']['path'], 'relation.properties']))


def regenerate(argv):
    """Deletes old data and regenerates new models using a sequence of steps.

    Args:
        argv: An object with the command line arguments.

    """
    print('This command requires: Google Parsey, Stanford CoreNLP.')

    print('Cleaning existing data...')
    clean_data()

    print('Generating TSV file from annotated data...')
    transform_ner_from_standoff(''.join([dirs['transformed']['path'], 'dblp.tsv']))

    print("Generating Part Of Speech tag using Google's Tensorflow and Syntaxnet...")
    run_google(argv)

    print("Generating Stanford's NER inputfile...")
    merge_pos(''.join([dirs['transformed']['path'], 'noempty.tsv']),
              ''.join([dirs['transformed']['path'], 'pos-noempty.tsv']),
              ''.join([dirs['transformed']['path'], 'stanford-ner-input.tsv']))

    print("Generating CORPUS Roth and Yih's Stanford REL inputfile...")
    transform_rel_from_standoff(''.join([dirs['transformed']['path'], 'stanford-rel-input.corp']),
                                ''.join([dirs['transformed']['path'], 'pos-noempty.tsv']))

    print("Generating Model using CRFClassifier Stanford's NER...")

    train_stanford_ner()

    print("Generating Model using MachineReading Stanford's REL...")
    train_stanford_rel()
