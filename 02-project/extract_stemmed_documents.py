from os import makedirs
from os.path import join
from re import split

from argparse import ArgumentParser

def extract_stemmed_documents(input_path, output_directory):
    makedirs(output_directory, exist_ok=True)
    with open(input_path, 'r') as infile:
        documents_string = infile.read()
        it = iter(split(r"\# ([0-9]+)\n", documents_string))
        next(it)
        for doc_num in it:
            filename = 'CACM-%04d.txt' % int(doc_num)
            with open(join(output_directory, filename), 'w') as outfile:
                outfile.write(next(it).strip())

parser = ArgumentParser(description='Extracts the stemmed documents to a directory.')
parser.add_argument("stemmed_document_file", help="the path to the stemmed document file to extract")
parser.add_argument("output_directory", help="the path to write the extracted files to")

args = parser.parse_args()

extract_stemmed_documents(args.stemmed_document_file, args.output_directory)