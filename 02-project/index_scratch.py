from lib.from_scratch.indexer import index_documents, write_index, write_positional_index, write_term_counts

from argparse import ArgumentParser

parser = ArgumentParser(description='Creates and outputs aninverted index from a directory of parsed, tokenized text files.')
parser.add_argument("input_directory", help="the directory to read text files from")
parser.add_argument("--uni", help="the output file for writing the unigram index")
parser.add_argument("--bi", help="the output file for writing the bigram index")
parser.add_argument("--tri", help="the output file for writing the trigram index")
parser.add_argument("--pos", help="the output file for writing the positional index")
parser.add_argument("--termcounts", help="the output file (CSV) for writing the count of terms in each document (includes non-unique terms)")

args = parser.parse_args()

# Index the documents
index_documents(args.input_directory)

# Write indexes
if args.uni is not None:
    write_index(args.uni, n=1)
if args.bi is not None:
    write_index(args.bi, n=2)
if args.tri is not None:
    write_index(args.tri, n=3)

# Write positional index for unigrams
if args.pos is not None:
    write_positional_index(args.pos)

# Write the [Document ID, Term count] table
if args.termcounts is not None:
    write_term_counts(args.termcounts, human_readable=False)