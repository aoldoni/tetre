"""Directory folders

This directory is a configuration file for all paths used by this application.

Todo:
    * Remove old style global variable filenames and use dictionary structure instead.

"""

dirs = {
    'models':                   {'path': 'models/'},
    'config':                   {'path': 'config/'},
    'annotated':                {'path': 'training/annotated/'},
    'transformed':              {'path': 'training/transformed/'},
    'microsoft_data':           {'path': 'training/gazette/microsoft_academic_data/'},
    'downloaded':               {'path': 'data/input/downloaded/text/'},
    'google_parsey_path':       {'path': 'parsey/models/syntaxnet/'},
    'stanford_path':            {'path': 'stanford/stanford-corenlp-full-2015-12-09/'},
    'output_openie':            {'path': 'output/openie/'},
    'output_rel':               {'path': 'output/rel/'},
    'output_ngram':             {'path': 'output/ngram/'},
    'output_html':              {'path': 'output/html/'},
    'output_cache':             {'path': 'output/cache/'},
    'output_comparison':        {'path': 'output/comparison/sentences/'},
    'output_allenai_openie':    {'path': 'output/comparison/allenai_openie/'},
    'output_stanford_openie':   {'path': 'output/comparison/stanford_openie/'},
    'output_mpi_clauseie':      {'path': 'output/comparison/mpi_clauseie/'},
    'raw_input':                {'path': 'input/'},
    'html_templates':           {'path': 'templates/'}
}


models = 'models/'
config = 'config/'

annotated       = 'training/annotated/'
transformed     = 'training/transformed/'
microsoft_data  = 'training/gazette/microsoft_academic_data/'

downloaded = 'downloaded/'

google_parsey_path  = 'parsey/models/syntaxnet/'
stanford_path       = 'stanford/stanford-corenlp-full-2015-12-09/'

output_openie   = 'output/openie/'
output_rel      = 'output/rel/'
output_ngram    = 'output/ngram/'
output_html     = 'output/html/'
output_cache    = 'output/cache/'

output_comparison       = 'output/comparison/sentences/'
output_allenai_openie   = 'output/comparison/allenai_openie/'
output_stanford_openie  = 'output/comparison/stanford_openie/'
output_mpi_clauseie     = 'output/comparison/mpi_clauseie/'

raw_input = 'input/'

html_templates = 'templates/'
