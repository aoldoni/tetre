#!/usr/bin/env python

import sys
import os
import csv
import itertools

from internallib.directories import *

topics = ['Natural language', 'Database', 'Algorithm', 'Data Stru', 'Machine Learning', \
            'Data warehous', 'Indexing', 'Big Data', 'Data Mi', 'Search Engine', \
            'Social Choice', 'Information Retrieval']

def regenerate(argv):
    fields_study_hierarchy = 'FieldOfStudyHierarchy/FieldOfStudyHierarchy.txt'
    fields_study = 'FieldsOfStudy/FieldsOfStudy.txt'
    paper_keywords = 'PaperKeywords/PaperKeywords.txt'

    fields_array = {}
    db_fields = {}
    db_keywords = {}

    concepts_set = set()

    with open(microsoft_data+fields_study, 'r') as input_lists, \
        open(microsoft_data+fields_study_hierarchy, 'r') as input_hierarchy, \
        open(microsoft_data+paper_keywords, 'r') as input_keywords:
        
        database_ids = []

        for line in input_lists:
            output_line_split = line.strip().split('\t')
            fields_array[output_line_split[0]] = output_line_split[1]

            for topic in topics:
                if (topic.lower() in output_line_split[1].lower()):
                    concepts_set.add(fields_array[output_line_split[0]].upper())
                    database_ids.append(output_line_split[0])

        print "Generate a gazette with topics", database_ids

        print "Initial concept set", concepts_set

        for hierarchy_line in input_hierarchy:
            output_line_split = hierarchy_line.strip().split('\t')

            # if (output_line_split[0] == database_ids):
            #     print output_line_split, fields_array[output_line_split[2]]

            if (output_line_split[2] in database_ids):
                db_fields[output_line_split[0]] = fields_array[output_line_split[0]]
                concepts_set.add(fields_array[output_line_split[0]].upper())
                # print output_line_split, fields_array[output_line_split[0]]

        print "Expanded concept set", concepts_set

        i = 0
        for keywords_line in input_keywords:
            output_line_split = keywords_line.strip().split('\t')

            if (output_line_split[2] in db_fields):
                # db_keywords[i] = output_line_split[1]
                concepts_set.add(output_line_split[1].upper())
                i = i+1

                # print [output_line_split[1], db_fields[output_line_split[2]]]

    with open(microsoft_data+'gazette.txt', 'w') as output:
        for concept in concepts_set:
            output.write("CONCEPT " + concept + "\n")

    return

if __name__ == '__main__':
    sys.exit(regenerate(sys.argv))
