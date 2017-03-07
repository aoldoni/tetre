"""Directory folders

This directory is a configuration file for all paths used by this application.

Todo:
    * Remove old style global variable filenames and use dictionary structure instead.

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


# models = 'models/'
# config = 'config/'
#
# annotated       = 'training/annotated/'
# transformed     = 'training/transformed/'
# microsoft_data  = 'training/gazette/microsoft_academic_data/'
#
# downloaded = 'downloaded/'
#
# google_parsey_path  = 'parsey/models/syntaxnet/'
# stanford_path       = 'stanford/stanford-corenlp-full-2015-12-09/'
#
# output_openie   = 'output/openie/'
# output_rel      = 'output/rel/'
# output_ngram    = 'output/ngram/'
# output_html     = 'output/html/'
# output_cache    = 'output/cache/'
#
# output_comparison       = 'output/comparison/sentences/'
# output_allenai_openie   = 'output/comparison/allenai_openie/'
# output_stanford_openie  = 'output/comparison/stanford_openie/'
# output_mpi_clauseie     = 'output/comparison/mpi_clauseie/'
#
# raw_input = 'input/'
#
# html_templates = 'templates/'
