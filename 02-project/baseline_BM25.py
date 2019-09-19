from lib.from_scratch.indexer import read_term_counts, read_index

from argparse import ArgumentParser

parser = ArgumentParser(description='Performs queries from a query file using a BM25 retrieval model.')
parser.add_argument("index_path", help="the path to read the index from")
parser.add_argument("term_counts_path", help="the path to read the term counts from")
parser.add_argument("query_file_path", help="the path to a TSV query file containing query IDs and stopped, case-folded test queries")
parser.add_argument("-r", help="the number of scores to output for each query", type=int, default=None)
parser.add_argument("-k1", help="the k1 value", type=float, default=1.2)
parser.add_argument("-b", help="the b value", type=float, default=0.75)
parser.add_argument("-k2", help="the k2 value", type=float, default=100)

args = parser.parse_args()

# Read the term counts
read_term_counts(args.term_counts_path)
read_index(args.index_path)

from lib.from_scratch.retrieval_model import BM25RetrievalModel

# Create the retrieval model
model = BM25RetrievalModel()
model.k1 = args.k1
model.b = args.b
model.k2 = args.k2

# Perform the retrieval
model.process_query_file(args.query_file_path, 100)
