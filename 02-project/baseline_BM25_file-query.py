from lib.from_scratch.indexer import read_term_counts, read_index

from csv import reader as csv_reader

from argparse import ArgumentParser

parser = ArgumentParser(description='Performs queries from a file using a BM25 retrieval model w/ user interface.')
parser.add_argument("index_path", help="the path to read the index from")
parser.add_argument("term_counts_path", help="the path to read the term counts from")
parser.add_argument("query_file_path", help="the path to a TSV query file containing query IDs and stopped, case-folded test queries")
parser.add_argument("files_path", help="the path to the documents (must be named with doc id)")
parser.add_argument("files_ext", help="the extension for the documents")
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

with open(args.query_file_path) as query_file:
    reader = csv_reader(query_file, delimiter='\t')
    for query_row in reader:
        query_id = query_row[0]
        query_string = query_row[1].strip()
        print("QUERY: %s" % query_id)
        # Perform the retrieval
        model.display_documents(query_string, args.files_path, args.files_ext, num_results=args.r)