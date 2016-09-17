# TOOLKIT FOR EXPLORING TEXTS FOR RELATION EXTRACTION

These scripts help utilising existing tools in the task of information extractino in a new corpus. They are mostly standalone commandline tools and functions that do data transformation, and parsing/preparation, while also invoking some other selected third party tools.


# INSTALLATION

- Download this toolkit:  
    `git clone https://github.com/aoldoni/comp9596.git .`

- Create directories and prepare assets data:  
    `mkdir data models parsey stanford training`  
    `mkdir data/input data/output data/downloaded`  
    `mkdir data/output/html data/output/ngram data/output/openie data/output/rel`  
    `cp -R templates/assets data/output/html/assets`

The next steps depend on what you will be trying to run. In case of MacOS, uou might want to replace some of these steps with using `brew`. Information to installing brew can be found at http://brew.sh/.


## INSTALLATION PYTHON DEPENDENCIES

- Install Python: http://docs.python-guide.org/en/latest/starting/installation/
    - This program expects Python 2 to be running as `python`.
    - This program expects Python 3 (at least 3.4) to be running as `python3`.

- Install PIP: https://pip.pypa.io/en/stable/installing/ - please install it using `python3` so all packages will be installed under the new version. This is important since if you install pip under `python` (i.e. for Python 2) the packages installed will not work in the python3 version of the code.

E.g.:  
    `python3 get_pip.py`

- Install the following Python/Python3 modules:  
    - requests
    - BeautifulSoup4

E.g.:  
    `python3 -m pip requests BeautifulSoup4`

- Install Graphviz binaries: http://www.graphviz.org/Download..php


## INSTALLATION MAIN PACKAGES

- Install Spacy, Virtualenv, and Spacy's English model: https://spacy.io/docs/#getting-started
- Install NLTK (as a python3 module): http://www.nltk.org/install.html
- Install Brat 1.3 Crunchy Frog: http://brat.nlplab.org/installation.html
- Install the following Python/Python3 modules:
    - nltk
    - corpkit
    - corenlp-xml
    - django
    - graphviz

E.g.:  
    `python3 -m pip nltk corpkit corenlp-xml`


## INSTALLATION STANFORD'S CORENLP

1. Install Java: http://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html
2. Install Maven: https://maven.apache.org/install.html

3. Move into created directory:  
    `cd stanford`

4. Download the jars for:
    - NER
    - Full CoreNLP

5. Extract them inside the stanford folder, thus having the following subdirectories:
    - `stanford/stanford-corenlp-full-2015-12-09`
    - `stanford/stanford-ner-2015-12-09`

6. Inside `stanford/stanford-corenlp-full-2015-12-09/src` replace the code with:  
    `cd stanford/stanford-corenlp-full-2015-12-09/src`  
    `rm -rf *`  
    `git clone https://github.com/aoldoni/comp9596-stanford-corenlp-full`  

7. `cd ../../..`

8. Run `recompile_stanford.py`

9. The file `stanford/stanford-corenlp-full-2015-12-09/stanford-corenlp-dblp.jar` should now exist.


## INSTALLATION GOOGLE'S PARSEY

- Move into created directory:  
    `cd parsey`

- Install Google Syntaxnet: https://github.com/tensorflow/models/tree/master/syntaxnet#installation


# SCRIPTS AND PURPOSE

Scripts entry points are listed below with the intentions in a somewhat useful order:
- `get_data.py` : Download data form the txt output server.
- `corpus_analysis.py` : Generate data on the details of a given relationship.
- `process_gazette.py` : Generate the gazette from the Microsoft academic data.
- `find_relations.py` : Find the relations using either Stanford's OpenIE or Relation Extractor.
- `process_relations.py` : Heuristics for OpenIE output processing. E.g.: Allows you to only keep relatinos with at least one NER recognized entity.
- `recompile_stanford.py` : Recompile Stanford's full CoreNLP using Maven. This is needed for non-standard labels for NER.
- `regenerate_models.py` : Regenerates the models to be used in the Stanford's CoreNLP based on anotated from Brat.

Paths and dependencies are maintained inside `internalib/directories.py`.


# USAGE

## ANALYSE A RELATION

1. Run `./get_data data`
2. All the papers "related.txt" should now be in the `data/downloaded` folder.
3. Move all `txt` files from `data/downloaded` to `data/input`.
4. Make sure you are inside the proper Virtualenv from Spacy (e.g.: `source .env/bin/activate`).
5. Run:  
    `./corpus_analysis.py data improves -g -format dep_,pos_ -behaviour groupby`

Notes:
- Change the behaviour to `-behaviour accumulator` as to show the accumlated tree with the occurrencies of the dependency tree and part-of-speech tags.
- Change the command to `-format dep_,pos_ -behaviour simplified_groupby` so you can apply simplificatino rules in the trees.

The script behaviour is to simply replace the content of the output folder (normally `data/output/html`) with newly generated, so please backup the outputs as you go. Please leave the `assets` folder inside `data/output/html`.

The word `improves` can also be changed to any word.


# NOTES

- This toolkit already contains an enhanced version of Sampo Pyysalo's library https://github.com/spyysalo/standoff2conll which generates files in the Stanford's Relation Extractor training formar, based on the Brat's annotation standoff format.