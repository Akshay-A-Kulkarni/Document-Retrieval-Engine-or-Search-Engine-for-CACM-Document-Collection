from lib.shared_utils.article_processor import process_directory

from argparse import ArgumentParser

parser = ArgumentParser(description='Preprocesses CACM documents by tokenizing, removing non-alphanumeric characters, performing case folding, and removing trailing digit tokens at end of file.')
parser.add_argument("input_directory", help="the path to read the CACM documents from")
parser.add_argument("output_directory", help="the path to output processed documents to")

args = parser.parse_args()

process_directory(args.input_directory, args.output_directory)