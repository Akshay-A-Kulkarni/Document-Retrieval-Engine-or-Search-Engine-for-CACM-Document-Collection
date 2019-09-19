from lib.from_scratch.indexer import read_term_counts, read_index

from argparse import ArgumentParser

parser = ArgumentParser(description='Performs queries from a query file using a Vector Space retrieval model.')
parser.add_argument("index_path", help="the path to read the index from")
parser.add_argument("term_counts_path", help="the path to read the term counts from")
parser.add_argument("query_file_path", help="the path to a TSV query file containing query IDs and stopped, case-folded test queries")
parser.add_argument("-r", help="the number of scores to output for each query", type=int, default=None)
parser.add_argument("-rel", help="the path to a cacm relevance file to enable optimal query transformation using Rocchio's Algorithm", default=None)

args = parser.parse_args()

# Read the term counts
read_term_counts(args.term_counts_path)
read_index(args.index_path)

from lib.from_scratch.retrieval_model import VectorSpaceRetrievalModel

# Create the retrieval model
model = VectorSpaceRetrievalModel()

# Perform the retrieval
model.process_query_file(args.query_file_path, args.rel, args.r)