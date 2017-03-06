import os
import csv

from standoff2other.postag import syntaxnet_split_list
# from standoff2other.standoff2conll import conversion_entry, OUTPUT_TYPES
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

    While the library is executed externally given python3 vs. python2 compatibility issues,
    note that the library version of the entry point call is left commented below for future reference.

    Args:
        file: A string with the directory to be transformed.

    """

    # alternative as library for the following command line
    command_line = ''.join(['./' + dirs['standoff2other_path']['path'] + 'standoff2conll.py ',
                        dirs['annotated']['path'], ' ',
                        ' > ' + dirs['transformed']['path'] + 'documents.tsv'])
    print(command_line)
    os.system(command_line)

    # from logging import error
    # with open(file, 'w') as output:
    #     data = conversion_entry([dirs['annotated']['path']], OUTPUT_TYPES['CONLL'])
    #     if data:
    #         output.write(data)
    #     else:
    #         error("No data could be written, please check if Brat input is in the correct folder.")


def transform_rel_from_standoff(file, file_postags):
    """Entry point for data transformation.

    Entry point as to transform annotated Brat files (standoff format) to
    Stanford's Relation Extractor training format.

    While the library is executed externally given python3 vs. python2 compatibility issues,
    note that the library version of the entry point call is left commented below for future reference.

    Args:
        file: A string with the directory to be transformed.
        file_postags: A string with the file with the POS tags.

    """
    # alternative as library for the following command line
    command_line = ''.join(['./' + dirs['standoff2other_path']['path'] + 'standoff2conll.py ',
                       dirs['annotated']['path'], ' ',
                       '--process ROTHANDYIH ',
                       '--process_pos_tag_input ',
                       file_postags,
                       ' > ' + dirs['transformed']['path'] + 'stanford-rel-input.corp'])
    print(command_line)
    os.system(command_line)

    # from logging import error
    # with open(file, 'w') as output:
    #     data = conversion_entry([dirs['annotated']['path']], OUTPUT_TYPES['ROTHANDYIH'], file_postags)
    #     if data:
    #         output.write(data)
    #     else:
    #         error("No data could be written, please check if Brat input is in the correct folder.")


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
                   "documents.tsv | awk '{ print $1 }' | syntaxnet/google.sh 1>", root_dir_distance,
                   dirs['transformed']['path'], 'pos.tsv']))
    os.system(''.join(['cat ', root_dir_distance, dirs['transformed']['path'],
                       "documents.tsv | awk '{ print $1 }' | syntaxnet/google.sh 1>", root_dir_distance,
                       dirs['transformed']['path'], 'pos.tsv']))

    # remove empty lines
    os.system(''.join(["awk 'NF' ", root_dir_distance, dirs['transformed']['path'],
                      'documents.tsv > ', root_dir_distance, dirs['transformed']['path'], 'noempty.tsv']))
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


def merge_pos(f1, f2, output_file):
    """Merge 2 column-based files into 1.

    File 1 is expected to be in the following tab-separated format below. Note that it simply contains a
    word followed by its label, or "O" for other.

RELATED	O
WORK	O
LSH	Concept
functions	Concept
are	O
introduced	O

    File 2 is expected to be in the following tab-separated format below. Note that this is
    the raw output from Google's Parsey Tensorflow model.

1	RELATED	_	VERB	VBN	_	0	ROOT	_	_
1	WORK	_	VERB	VB	_	0	ROOT	_	_
1	LSH	_	NOUN	NNP	_	0	ROOT	_	_
1	functions	_	NOUN	NNS	_	0	ROOT	_	_
1	are	_	VERB	VBP	_	0	ROOT	_	_
1	introduced	_	VERB	VBN	_	0	ROOT	_	_

    The output then will contain all columns from f1, plus the fourth column
    of f2.

    Note that Parsey can split words, and the word found so far is noted in the
    syntaxnet_split_list list.

    Args:
        f1: The first file to be merged with.
        f2: The second file to merge.
        output_file: The output file name with the result of the merging.

    """

    with open(f1, 'r') as file1, \
            open(f2, 'r') as file2, \
            open(output_file, 'w') as output:

            reader1 = csv.reader(file1, delimiter='\t')
            reader2 = csv.reader(file2, delimiter='\t')

            it1 = iter(reader1)
            it2 = iter(reader2)

            for x, y in zip(it1, it2):
                x1, x2 = x

                if x1 in syntaxnet_split_list:
                    y = next(it2)

                y4 = y[4]
                output.write('\t'.join([x1, x2, y4]) + os.linesep)


def regenerate(argv):
    """Deletes old data and regenerates new models using a sequence of steps.

    Args:
        argv: An object with the command line arguments.

    """
    print('This command requires: Google Parsey, Stanford CoreNLP.')

    print('Cleaning existing data...')
    clean_data()

    print('Generating TSV file from annotated data...')
    transform_ner_from_standoff(''.join([dirs['transformed']['path'], 'documents.tsv']))

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
