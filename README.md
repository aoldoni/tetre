TOOLKIT FOR EXPLORING TEXTS FOR RELATION EXTRACTION
---------------------------------------------------

These scripts help utilising existing tools in the task of information extractino in a new corpus. They are mostly standalone commandline tools and functions that do data transformation, and parsing/preparation, while also invoking some other selected third party tools.


INSTALLATION BASE
-----------------

- Download this toolkit:
    `git clone https://github.com/aoldoni/comp9596.git .`

- Create directotories:
    `mkdir data models parsey stanford training`

The next steps depend on what you will be trying to run. In case of MacOS, uou might want to replace some of these steps with using `brew`. Information to installing brew can be found at http://brew.sh/.


INSTALLATION SPACY AND PYTHON DEPENDENCIES
------------------------------------------

- Install Python: http://docs.python-guide.org/en/latest/starting/installation/
    - This program expects Python 2 to be running as `python`.
    - This program expects Python 3 to be running as `python3`.

- Install PIP: https://pip.pypa.io/en/stable/installing/
- Install Spacy and Virtualenv: https://spacy.io/docs/#getting-started
- Install NLTK: http://www.nltk.org/install.html
- Install Brat 1.3 Crunchy Frog: http://brat.nlplab.org/installation.html


INSTALLATION STANFORD'S CORENLP
-------------------------------

- Install Java: http://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html
- Install Maven: https://maven.apache.org/install.html

- Move into created directory:
    `cd stanford`

- Download the jars:
    - 



INSTALLATION GOOGLE'S PARSEY
-------------------------------
    `cd parsey`



SCRIPTS AND PURPOSE
-------------------

Scripts are listed below with the intentions in a somewhat useful order:
- corpus_analysis.py
- find_relations.py
- get_data.py
- process_gazette.py
- process_relations.py
- recompile_stanford.py
- regenerate_models.py

Paths and dependencies are 

USAGE
-----

NOTES
-----
- This toolkit already contains an altered versino of Sampo Pyysalo's library https://github.com/spyysalo/standoff2conll which generates files in the Stanford's Relation Extractor based on the Brat's annotation standoff format.