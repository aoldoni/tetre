import os

from directories import dirs
from openie import openie_to_pretty


def run_relations_separate_output(argv):

    for fn in os.listdir(dirs['raw_input']['path']):
        if fn == ".DS_Store":
            continue

        name = dirs['raw_input']['path'] + fn

        if not argv.brat_to_stanford_use_model:
            print("Running Stanford's OpenIE (1 per file mode)...")
            
            output_name = dirs['output_openie']['path'] + fn + '.tsv.original'
            output_processed = dirs['output_openie']['path'] + fn + '.tsv.easy'

            print("Will write to files:")
            print(output_name)
            print(output_processed)

            os.system(''.join(['java -cp ',
                               dirs['stanford_corenlp_path']['path'] + '*:',
                               dirs['stanford_ner_path']['path'] + 'lib/*',
                               '-Xmx8g ',
                               'edu.stanford.nlp.naturalli.OpenIE ',
                               '-props ' + dirs['config']['path'] + 'pipeline-openie.properties ',
                               name,
                               ' 1>' + output_name]))

            with open(output_name, 'r') as input_file, open(output_processed, 'w') as output_file:
                for line in input_file.readlines():
                    output_line_split = line.split('\t')
                    output_line = openie_to_pretty(output_line_split)
                    output_file.write(output_line + "\n")

        else:
            print("Running Stanford's Relation Extractor (1 per file mode)...")
            os.system(''.join(['java -cp ',
                               dirs['stanford_corenlp_path']['path'] + '*:',
                               dirs['stanford_ner_path']['path'] + 'lib/* ',
                               '-Xmx8g ',
                               'edu.stanford.nlp.pipeline.StanfordCoreNLP ',
                               '-props ' + dirs['config']['path'] + 'pipeline.properties ',
                               '-file ', name]))

    return


def run_relations(argv):
    names = []
    filename = 'filelist.txt'

    for fn in os.listdir(argv.directory + dirs['raw_input']['path']):
        if fn == ".DS_Store":
            continue

        names.append(dirs['raw_input']['path'] + fn)

    with open(filename, 'w') as output:
        data = "\n".join(names)
        output.write(data)

    if not argv.brat_to_stanford_use_model:
        print("Running Stanford's OpenIE... (Bulk mode)")
        os.system(''.join(['java -cp ',
                           dirs['stanford_corenlp_path']['path'] + '*:',
                           dirs['stanford_ner_path']['path'] + 'lib/* ',
                           '-Xmx8g ',
                           'edu.stanford.nlp.naturalli.OpenIE ',
                           '-props ' + dirs['config']['path'] + 'pipeline-openie.properties ',
                           '-filelist ' + filename + ' 1>' + dirs['output_openie']['path'] + '/output.tsv']))

    else:
        print("Running Stanford's Relation Extractor... (Bulk mode)")
        os.system(''.join(['java -cp ',
                           dirs['stanford_corenlp_path']['path'] + '*:',
                           dirs['stanford_ner_path']['path'] + 'lib/* ',
                           '-Xmx8g ',
                           'edu.stanford.nlp.pipeline.StanfordCoreNLP ',
                           '-props ' + dirs['config']['path'] + 'pipeline.properties ',
                           '-filelist ' + filename]))

    os.remove(filename)

    return


def run(argv):

    if argv.brat_to_stanford_bulk_processing:
        run_relations(argv)
    else:
        run_relations_separate_output(argv)
