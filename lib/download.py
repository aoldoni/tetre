import requests
from bs4 import BeautifulSoup
from lib import directories


def get_all_related(base_url):
    """Scraps the UNSW webserver using BeautifulSoup to find the relevant files.

    In this server, files were exposed in an Apache-style directory listing, in which
    each directory contains subdirectories and so on in a structure for papers until
    the "relate.txt" file is found with the "Related Work" section of the academic paper.

    These papers were originally in the PDF format and then text was extracted from it
    using a complex process.

    Args:
        base_url: The server in question that will be scraped.

    Yields:
         :obj:`list`: An array containing the URL to be downloaded in position 0, and
            a positino 1 in which another array containing info about this file which
            will be concatenated to form the filename in disk.

    """
    soup = BeautifulSoup(requests.get(base_url).text, "html.parser")
    files_to_get = 'relate.txt'

    # a tags in level 0
    for a_l0 in soup.find('ul').find_all('a'):
        if a_l0['href'].endswith("/"):

            # ul tags in level 1
            soup_l1 = BeautifulSoup(requests.get(base_url + a_l0['href']).text, "html.parser")
            for a_l1 in soup_l1.find('ul').find_all('a'):
                if a_l1['href'].endswith("/"):

                    # a tags in level 2
                    soup_l2 = BeautifulSoup(requests.get(base_url + a_l0['href'] +
                                                         a_l1['href']).text, "html.parser")
                    for a_l2 in soup_l2.find('ul').find_all('a'):
                        if a_l2['href'].endswith("/"):

                            # a tags in level 3
                            soup_l3 = BeautifulSoup(requests.get(base_url + a_l0['href'] + a_l1['href'] +
                                                                 a_l2['href']).text, "html.parser")
                            for a_l3 in soup_l3.find('ul').find_all('a'):

                                # a tags in level 4
                                relate_url = base_url + a_l0['href'] + a_l1['href'] + a_l2['href'] + a_l3['href']

                                if a_l3['href'] == files_to_get:
                                    yield [relate_url, [a_l0['href'], a_l1['href'], a_l2['href'], a_l3['href']]]


def download_relate(relate_url):
    """Downloads a file given by a URL into a folder.

    Args:
        relate_url (:obj:`list`): An array containing the URL to be downloaded in position 0, and
            a positino 1 in which another array containing info about this file which
            will be concatenated to form the filename in disk.

    """
    contents = requests.get(relate_url[0]).text
    output_name = "_".join(relate_url[1]).replace("/", "")

    with open(directories.dirs['downloaded']['path'] + output_name, 'w') as output_file:
        output_file.write(contents)


def start(ap):
    """Module entry point for the command line.

    Args:
        ap (:obj:`ArgumentParser`): The command line parameters.

    """
    for relate_url in get_all_related(ap.url):
        download_relate(relate_url)
