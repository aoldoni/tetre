# TOOLKIT FOR EXPLORING TEXTS FOR RELATION EXTRACTION

These scripts help utilising existing tools in the task of information extraction in a new corpus composed of academic papers. They are mostly standalone commandline tools and functions that do data transformation, and parsing/preparation, while also invoking some other selected third party tools.

- Add link to master thesis https://raw.githubusercontent.com/aoldoni/comp9596-master-thesis/master/thesis.pdf

# INSTALLATION

- Download this toolkit:  
    `mkdir tetre`  
    `cd tetre`  
    `git clone https://github.com/aoldoni/tetre.git .`  

- Create directories (one single big command):  
    `./bin/tetre setup`
    
- Prepare the static assets link:  
    `cd data/output/html/`  
    `ln -s ../../../templates/assets/ assets`  
    `cd ../../..`  

The next steps depend on what you will be trying to run. In case of MacOS, you might want to replace some of these steps with using `brew`.
Information to installing brew can be found at http://brew.sh/.


## INSTALLATION PYTHON DEPENDENCIES

- Install Python: http://docs.python-guide.org/en/latest/starting/installation/
    - This program expects Python 2 to be running as `python`.
    - This program expects Python 3 (at least 3.4) to be running as `python3`.

- Install PIP: https://pip.pypa.io/en/stable/installing/ - please install it using `python3` so all packages will be installed under the new version. This is important since if you install pip under `python` (i.e. for Python 2) the packages installed will not work in the python3 version of the code. E.g.: `python3 get_pip.py`

- Create a virtual environment. From now onwards, all the package installations will only be available in this directory/virtual environment:  
    `virtualenv .env`  
    `source .env/bin/activate`  

- Install Graphviz binaries: http://www.graphviz.org/Download.php
- Install jq for the demo: https://stedolan.github.io/jq/ (or you might just want to pipe the TETRE output to `python -m json.tool` instead)

- Install the following Python/Python3 modules:  
    - requests
    - BeautifulSoup4

E.g.:  
    `python3 -m pip install requests BeautifulSoup4`


## INSTALLATION MAIN PACKAGES

- Install Spacy 0.101.0, Virtualenv, and Spacy's English model: https://spacy.io/docs/#getting-started
    `python3 -m pip install spacy==0.101.0`  
    
- Install NLTK (as a python3 module): http://www.nltk.org/install.html
- Install Brat 1.3 Crunchy Frog: http://brat.nlplab.org/installation.html
- Install the following Python/Python3 modules:
    - nltk
    - corpkit
    - corenlp-xml
    - django
    - graphviz

E.g.:  
    `python3 -m pip install nltk corpkit corenlp-xml django graphviz`


# INSTALLATION EXTERNAL PACKAGES 

These are optional packages, mostly if you want to explore available wrappers for the Stanford's relation extractor and NER processes, or
if you want to compare the TETRE output with the externally available tools.

IMPORTANT: You may skip to the (Hello World)[#hello-world] section below if your intention is simply to use TETRE stand-alone.


## INSTALLATION STANFORD'S CORENLP

1. Install Java: http://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html
2. Install Maven: https://maven.apache.org/install.html

3. Move into created directory:  
    `cd external/bin/stanford`

4. Download the jars for:
    - NER
    - Full CoreNLP

5. Extract them inside the respective folder folder, thus having the following subdirectories, respectivelly:
    - `external/bin/stanford/ner/`
    - `external/bin/stanford/corenlp/`

6. Inside `external/bin/stanford/corenlp/src` replace the code with:  
    `external/bin/stanford/corenlp/src`  
    `rm -rf *`  
    `git clone https://github.com/aoldoni/comp9596-stanford-corenlp-full`  

7. Return to root directory:
    `cd ../../../../../`

8. Install `ant` (e.g.: using `brew` or `apt-get`). Re-compile stanford's binaries:
    `./bin/tetre compile`

9. The file `external/bin/stanford/corenlp/stanford-corenlp-compiled.jar` should now exist.

## INSTALLATION GOOGLE'S PARSEY

- Move into created directory:  
    `cd external/bin/parsey`

- Install Google Syntaxnet: https://github.com/tensorflow/models/tree/master/syntaxnet#installation

- Copy custom initiator file for syntaxnet available inside this project into the correct directory:   
    `cp external/extra/google-parsey/google.sh external/bin/parsey/models/syntaxnet/syntaxnet/google.sh`

## INSTALLATION CLAUSEIE

- Move into created directory:  
    `cd external/bin/clausie`

- Download ClauseIE from http://resources.mpi-inf.mpg.de/d5/clausie/clausie-0-0-1.zip and extract into this folder.


## INSTALLATION ALLENAI OPENIE

- Move into created directory:  
    `cd external/bin/allenai_openie`

- Run installation process found in https://github.com/allenai/openie-standalone#command-line-interface


# HELLO WORLD

- Move your raw text data into `data/input/raw`:
    `cp -R my_raw_text_files/* data/input/raw/`

- Process your relation:

    `/bin/tetre extract --tetre_word improves --tetre_output json | jq ''`

- The output will be the JSON relations, such as:

```json
[
  {
    "other_relations": [],
    "relation": {
      "obj": "statistical machine translation methods",
      "rel": "improves",
      "subj": "noun phrase translation subsystem"
    },
    "rules_applied": "Growth.replace_subj_if_dep_is_relcl_or_ccomp,Subj.remove_tags",
    "sentence": "In addition, Koehn and Knight  show that it is reasonable to define noun phrase translation without context as an independent MT subtask and build a noun phrase translation subsystem that improves statistical machine translation methods.\n"
  },
  {
    "other_relations": [],
    "relation": {
      "obj": "chronological ordering significantly",
      "rel": "improves",
      "subj": "proposed algorithm"
    },
    "rules_applied": "Reduction.remove_tags,Obj.remove_tags,Subj.remove_tags",
    "sentence": "The evaluation results show that the proposed algorithm improves the chronological ordering significantly.\n"
  },
  {
    "other_relations": [],
    "relation": {
      "obj": "performance of the classifier over all categories",
      "rel": "improves",
      "subj": "combination of the two different types of representations"
    },
    "rules_applied": "Reduction.remove_tags,Obj.remove_tags,Subj.remove_tags",
    "sentence": "They show that concept-based representations can outperform traditional word-based representations, and that a combination of the two different types of representations improves the performance of the classifier over all categories.\n"
  },
  ...
```

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
6. To analyse the subj relation instead run:  
    `./corpus_analysis.py data improves -g -behaviour_root subj` 

Notes:
- Change the behaviour to `-behaviour accumulator` as to show the accumlated tree with the occurrencies of the dependency tree and part-of-speech tags.
- Change the command to `-format dep_,pos_ -behaviour simplified_groupby` so you can apply simplificatino rules in the trees.

The script behaviour is to simply replace the content of the output folder (normally `data/output/html`) with newly generated, so please backup the outputs as you go. Please leave the `assets` folder inside `data/output/html`.

The word `improves` can also be changed to any word.  

## INCORPORATE RESULTS FROM OTHER TOOLS

1. Run the below to prepare the segmented sentences for the relation being searched for:  
    `./corpus_analysis.py data improves -p`

2. Run the below to execute the external tool:  
    `./corpus_analysis.py data improves -r -rw AllenAIOpenIE`

3. Re-run the below to incorporate results from external tools:  
    `./corpus_analysis.py data improves -g -i`

4. Or generate a sample HTML with CSV document for marking:  
    `./corpus_analysis.py data improves -g -i -sampling 6.5 -seed 99879 -output html_csv`

Notes:
- Other options are AllenAIOpenIE, MPICluaseIE or StanfordOpenIE.
- Once all systems are executed with the -r and -rw parameters, once you run the system with -g parameter again, the external results will be incorporated in the HTML.


## OTHER USAGES

Simplified command using default parameters:  
- `./corpus_analysis.py data improves -g -output html`

Force reprocessing:  
- `./corpus_analysis.py data improves -g -output html -f`

Different output:  
- `./corpus_analysis.py data improves -g -output json`

Different output, JSON pretty output:  
- `./corpus_analysis.py data improves -g -output json | python -m json.tool`

# NOTES

- This toolkit already contains an enhanced version of Sampo Pyysalo's library https://github.com/spyysalo/standoff2conll which generates files in the Stanford's Relation Extractor training formar, based on the Brat's annotation standoff format.
- Add a note regarding the customizations needed for the Relation Extractor. https://github.com/stanfordnlp/CoreNLP/issues/359
- Add a note in here on how to use my custom stanford src code as to re-compile stanford corenlp, and specify the older 2016 versino.

- Add an example on how to add a new growth/reduction/child rule.