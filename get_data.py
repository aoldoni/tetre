#!/usr/bin/env python3

import sys
import requests
from bs4 import BeautifulSoup
from internallib.directories import *

default_url = 'http://43.240.97.125:8008/'

def get_all_related():
    soup = BeautifulSoup(requests.get(default_url).text, "html.parser")

    for a_l0 in soup.find('ul').find_all('a'):
        if a_l0['href'].endswith("/"):

            soup_l1 = BeautifulSoup(requests.get(default_url + a_l0['href']).text, "html.parser")
            for a_l1 in soup_l1.find('ul').find_all('a'):
                if a_l1['href'].endswith("/"):

                    soup_l2 = BeautifulSoup(requests.get(default_url + a_l0['href'] + a_l1['href']).text, "html.parser")
                    for a_l2 in soup_l2.find('ul').find_all('a'):
                        if a_l2['href'].endswith("/"):

                            soup_l3 = BeautifulSoup(requests.get(default_url + a_l0['href'] + a_l1['href'] + a_l2['href']).text, "html.parser")
                            for a_l3 in soup_l3.find('ul').find_all('a'):

                                relate_url = default_url + a_l0['href'] + a_l1['href'] + a_l2['href'] + a_l3['href']
                                
                                if a_l3['href'] == 'relate.txt':
                                    yield [relate_url, [a_l0['href'] , a_l1['href'] , a_l2['href'] , a_l3['href']] ]

    return

def download_relate(args, relate_url):
    contents = requests.get(relate_url[0]).text
    output_name = "_".join(relate_url[1]).replace("/", "")

    # print(relate_url[0])
    # print(args.directory + downloaded + output_name)

    with open(args.directory + downloaded + output_name, 'w') as output_file:
        output_file.write(contents)

    return

def argparser():
    import argparse
    ap = argparse.ArgumentParser(description='Get all online data form ' + default_url,
                                 usage='%(prog)s DIRECTORY')
    ap.add_argument('directory')
    return ap

def main(argv):
    args = argparser().parse_args(argv[1:])
    
    if (not args.directory.endswith("/")):
        args.directory = args.directory + "/"

    for relate_url in get_all_related():
        download_relate(args, relate_url)


if __name__ == '__main__':
    sys.exit(main(sys.argv))