from lib.lucene.basic_index_query import index_documents

from argparse import ArgumentParser

parser = ArgumentParser(description='Indexes documents from a directory of raw text (.txt) files.')
parser.add_argument("input_directory", help="the directory to read HTML files from (will only read files with .html extension)")
parser.add_argument("index_path", help="the path to write the index to")

args = parser.parse_args()

# Index the documents
index_documents(args.input_directory, args.index_path)