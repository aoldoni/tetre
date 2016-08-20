import os
import csv
import itertools

syntaxnet_split_list = ["cannot"]

def merge_pos(f1, f2, outputfile):
    with open(f1,'r') as file1, \
            open(f2,'r') as file2, \
            open(outputfile,'w') as output: 
            reader1 = csv.reader(file1, delimiter='\t')
            reader2 = csv.reader(file2, delimiter='\t')

            it1 = iter(reader1)
            it2 = iter(reader2)

            for x, y in itertools.izip(it1, it2):
                x1, x2 = x

                if x1 in syntaxnet_split_list:
                    y = next(it2)

                y4 = y[4]
                output.write('\t'.join([x1, x2, y4]) +  os.linesep)
