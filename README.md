1. run regenerate.py

java -cp stanford/stanford-corenlp-full-2015-12-09/*:stanford/stanford-ner-2015-12-09/lib/* -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP -props dblp-pipeline.properties

java -cp stanford/stanford-corenlp-full-2015-12-09/*:stanford/stanford-ner-2015-12-09/lib/* -Xmx4g edu.stanford.nlp.naturalli.OpenIE -props dblp-pipeline-openie.properties




Annotation:
- Parameters estart and eend is the multiple entities for REL.
- Debugging classifier, if it is not correct.
- Opulent verb - it is not very meaningful since it is too common.

Next steps:
    - Get older output, classify more papers and sent to Dr. Wei.
    - Try to find the source of the problem - for "it".

    - Disable of coref to simplify.
    - Customize the output of OpenIE.
    - Is there anything we can do to improve the output.
        - Can we see if OpenIE has entities?
        - Heuristics?
        - Use OpenIE input and filter out noises.

----------------------------

Possible approaches:
    - Gazette - Y

    - I think it was very clear from our meeting that the OpenIE tool is the more promising one. I just wonder at this point if we would “stop” any work on the Relation Extractor or advance on both in parallel. What I mean is:
    
    - Currently the only relations I annotate are “Improves / Worsen / IsA / Uses”. Moreover, in practice, unfortunately “Improves / Worsen” are not really seen too much. When then checking the “top 50” relations from the OpenIE, and ignoring the “opulent verbs” we find other relations such as: ('provide', 47), ('deﬁnes', 46), ('extend', 46), ('compute', 42), ('achieve', 42), ('builds on', 40), ('introduced', 38), ('consider', 38), ('using', 38), ('ﬁnd', 35), ('generate', 35), ('was', 34), ('store', 31), ('focuses on', 31), ('propose', 28), ('were', 26), ('accessing', 25), ('cleaning', 25) …. is there any value in going back from these "emerged” relations and, if they are correct, annotate the data to train the Relation Extractor?
    
    - Still I only annotated around 20 papers for training. At some point I remember you mentioned maybe we should annotate at least 100 to do a fair comparison between the methods (Ideally much much more, but given the constraints at least 100). Is it still correct? I.e.: In parallel, I should continue to manually annotate more data for the Relation Extractor model.

    - What could be our goal?
        - Make OpenIE fit a schema
        - Define a schema to be matched with openIE.
        - Strategy: accumlate the documents that actually contain these relations (biased, but OK for the purpose).
        - Then compare with Relatino Extractor in a text of 100 of these annotated relations.
        - Then do cross-validation and measure performance.

    Full path for maximization:
    - Use Stanfor NLP for POS
    - Rule Based NER? E.g.: match the gazette?
    - Global NER? E.g.: extract all the entities and then share these globally when filtering relations.

    Future work:
    - Other papers entity resolution:
        - add entities form other papers / trivial but would help a lot with meaning.
        - some papers don't name their processes.
    - Entity disambiguation.
    - Coref resolution.

----------------------------

- Debug some lines - line by line. Show the results form each classifier.
- Note the limitations:
    - Relation Extractor - just in the same sentences.
    - OpenIE - seem much more relevant results, but not involving entities. Just close relations, as there are 2 trainers, 1 to determine the sentence split. and another to have internal.

----------------------------

- Install standoff2conll
- Install corpkit
- Install corenlp-xml





ERRORS:
Processing file: data/input/acl_2014_P14-1105_relate.txt
Processing file: data/input/acl_2015_P15-1067_relate.txt
Processing file: data/input/emnlp_2006_W06-1622_relate.txt
Processing file: data/input/emnlp_2013_D13-1017_relate.txt
Broke in data/input/emnlp_2013_D13-1204_relate.txt