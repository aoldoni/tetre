import os

from directories import dirs
from parsers import should_skip_file


def run_relations_separate_output(argv):
    """Decides between running the model based Relation Extractor or OpenIE
    in separate output mode.

    Args:
        argv: An object with the command line arguments.

    """

    for fn in os.listdir(dirs['raw_input']['path']):
        if should_skip_file(fn):
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
    """Decides between running the model based Relation Extractor or OpenIE
    in bulk processing mode.

    Args:
        argv: An object with the command line arguments.

    """

    names = []
    filename = 'filelist.txt'

    for fn in os.listdir(dirs['raw_input']['path']):
        if should_skip_file(fn):
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
                           '-filelist ' + filename + ' 1>' + dirs['output_openie']['path'] + '/bulk_output.tsv']))

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
    """Decides between running the bullk_processing mode or per file mode:
        - Per file mode generates per file outputs in OpenIE, so better to match
        output to input.
        - Model based and OpenIE both can hang in the middle of processing if, e.g.:
        processing thousands of files.

    Args:
        argv: An object with the command line arguments.

    """
    if argv.brat_to_stanford_bulk_processing:
        run_relations(argv)
    else:
        run_relations_separate_output(argv)


def openie_to_pretty(entry):
    if len(entry) >=4:
        return entry[2].strip() + " ( " + entry[1].strip() + " , " + entry[3].strip() + " ) - " + entry[0].strip()
    return ""