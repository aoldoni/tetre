"""Directory folders

This directory is a configuration file for all paths used by this application.

"""

dirs = {
    'models':                   {'install': False, 'path': 'models/'},
    'config':                   {'install': False, 'path': 'config/'},

    'annotated':                {'install': True,  'path': 'data/input/training/annotated/'},
    'transformed':              {'install': True,  'path': 'data/input/training/transformed/'},
    'microsoft_data':           {'install': True,  'path': 'data/input/training/gazette/microsoft_academic_data/'},
    'downloaded':               {'install': True,  'path': 'data/input/downloaded/text/'},
    'raw_input':                {'install': True,  'path': 'data/input/raw/'},

    'google_parsey_path':       {'install': False, 'path': 'external/bin/parsey/models/syntaxnet',
                                 'root_distance': '../../../../../'},
    'google_parsey_root':       {'install': True,  'path': 'external/bin/parsey/'},
    'stanford_ner_path':        {'install': True,  'path': 'external/bin/stanford/ner/'},
    'stanford_corenlp_path':    {'install': True,  'path': 'external/bin/stanford/corenlp/'},
    'allenai_root':             {'install': True,  'path': 'external/bin/allenai/',
                                 'root_distance': '../../../'},
    'clauseie_root':            {'install': True,  'path': 'external/bin/clausie/'},

    'standoff2other_path':      {'install': True,  'path': 'external/lib/standoff2other/'},

    'output_openie':            {'install': True,  'path': 'data/output/openie/'},
    'output_rel':               {'install': True,  'path': 'data/output/rel/'},
    'output_ngram':             {'install': True,  'path': 'data/output/ngram/'},
    'output_html':              {'install': True,  'path': 'data/output/html/'},
    'output_cache':             {'install': True,  'path': 'data/output/cache/'},

    'output_comparison':        {'install': True,  'path': 'data/output/comparison/sentences/'},
    'output_allenai_openie':    {'install': True,  'path': 'data/output/comparison/allenai_openie/'},
    'output_stanford_openie':   {'install': True,  'path': 'data/output/comparison/stanford_openie/'},
    'output_mpi_clauseie':      {'install': True,  'path': 'data/output/comparison/mpi_clauseie/'},

    'html_templates':           {'install': False, 'path': 'templates/'}
}


def should_skip_file(fn):
    """List of file names that should skipped once looping through input files

    Args:
        fn: The filename to be checked.

    Returns:
        A boolean representing if the words should be skipped or not
     """
    jump_list = ["thumbs.db", ".DS_Store"]

    if any(fn in each_fn for each_fn in jump_list):
        return True
    else:
        return False
