from directories import dirs


topics = ['Natural language', 'Database', 'Algorithm', 'Data Stru', 'Machine Learning',
          'Data warehous', 'Indexing', 'Big Data', 'Data Mi', 'Search Engine',
          'Social Choice', 'Information Retrieval']


def generate_gazette():
    """Generate a gazette with keywords and concepts from the Microsoft Academic Data,
    given "topics" set in the topics variable.

    This will process 3 key files from the Microsoft Data dump, currently at:
        - https://www.microsoft.com/en-us/research/project/microsoft-academic-graph/
        - https://academicgraphaue.blob.core.windows.net/graph-2016-02-05/index.html

    Its schema is describe in the above link, but basically the field of study file
    contains the string of the field, e.g.: "Database" with its correspondent ID.

    The hierarchy file is simply a relation of IDs that form this hierarchy, and
    the PaperKeywords file would then list the keyords for each of these fields
    of study.

    And will transform into a Stanford Core NLP compatible gazette, with the following format:
     CONCEPT DATABASE
     CONCEPT ALGORITHM
     CONCEPT SEARCH ENGINE

    """

    fields_study_hierarchy = 'FieldOfStudyHierarchy/FieldOfStudyHierarchy.txt'
    fields_study = 'FieldsOfStudy/FieldsOfStudy.txt'
    paper_keywords = 'PaperKeywords/PaperKeywords.txt'

    fields_array = {}
    db_fields = {}

    concepts_set = set()

    with open(dirs['microsoft_data']['path'] + fields_study, 'r') as input_lists, \
            open(dirs['microsoft_data']['path'] + fields_study_hierarchy, 'r') as input_hierarchy, \
            open(dirs['microsoft_data']['path'] + paper_keywords, 'r') as input_keywords:
        
        database_ids = []

        print("Obtaining fields topics for gazette...")

        for line in input_lists:
            output_line_split = line.strip().split('\t')
            fields_array[output_line_split[0]] = output_line_split[1]

            for topic in topics:
                if topic.lower() in output_line_split[1].lower():
                    concepts_set.add(fields_array[output_line_split[0]].upper())
                    database_ids.append(output_line_split[0])

        print("Obtaining fields topics hierarchy concept set...")

        for hierarchy_line in input_hierarchy:
            output_line_split = hierarchy_line.strip().split('\t')

            if output_line_split[2] in database_ids:
                db_fields[output_line_split[0]] = fields_array[output_line_split[0]]
                concepts_set.add(fields_array[output_line_split[0]].upper())

        print("Obtaining keywords concept set... Warning: this may take a while.")

        i = 0
        for keywords_line in input_keywords:
            output_line_split = keywords_line.strip().split('\t')

            if output_line_split[2] in db_fields:
                concepts_set.add(output_line_split[1].upper())
                i += 1

    print("Generating concept gazette... Will write to " + dirs['microsoft_data']['path'] + 'gazette.txt')

    with open(dirs['microsoft_data']['path'] + 'gazette.txt', 'w') as output:
        for concept in concepts_set:
            output.write("CONCEPT " + concept + "\n")

    print("Finished.")


def run(argv):
    """Entry point for gazette generation.

    Args:
        argv: An object with the command line arguments.

    """
    generate_gazette()
