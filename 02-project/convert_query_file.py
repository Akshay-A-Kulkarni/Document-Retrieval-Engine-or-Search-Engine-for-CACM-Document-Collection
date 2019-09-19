from lib.shared_utils.convert_queries import convert_query_file

from argparse import ArgumentParser

parser = ArgumentParser(description='Converts the query file from XML format to TSV format.')
parser.add_argument("xml_file_path", help="the path to the XML query file to read")
parser.add_argument("tsv_file_path", help="the path to write the TSV query file to")
parser.add_argument("--stopwords", help="the path of a file with stop words")
parser.add_argument('--preventclean', help="prevents query cleaning and processing during conversion, except on existing whitespaces", action='store_false')

args = parser.parse_args()

convert_query_file(args.xml_file_path, args.tsv_file_path, args.stopwords, handlePunctuation=args.preventclean, foldcase=args.preventclean)
