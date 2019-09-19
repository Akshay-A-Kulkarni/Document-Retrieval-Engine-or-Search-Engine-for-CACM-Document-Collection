from lib.lucene.basic_index_query import process_query_file

from argparse import ArgumentParser

parser = ArgumentParser(description='Performs queries from a query file using a Lucene retrieval model.')
parser.add_argument("index_path", help="the path to read the index from")
parser.add_argument("query_file_path", help="the path to a TSV query file containing query IDs and stopped, case-folded test queries")
parser.add_argument("-r", help="the number of results to print per query", type=int, default=100)
parser.add_argument("-k", help="the number of top ranked documents to expand the query", type=int, default=0)
parser.add_argument("-n", help="the maximum number of terms to select for expanding queries from the top `k` documents", type=int, default=0)
parser.add_argument("-w", help="the path to the trained Word2Vec-trained word vectors (if provided, this will perform word embedding query expansion and ignore the arguments for pseudo-relevance feedback query expansion)")

args = parser.parse_args()

process_query_file(args.index_path, args.query_file_path, args.r, args.k, args.n, args.w)