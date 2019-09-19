import lucene
from collections import defaultdict
from csv import reader as csv_reader
from gensim.models import Word2Vec
from glob import glob
from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, TextField, StringField
from org.apache.lucene.index import DirectoryReader, IndexReader, IndexWriter, IndexWriterConfig, Term
from org.apache.lucene.queryparser.simple import SimpleQueryParser
from org.apache.lucene.search import BooleanClause, BooleanQuery, IndexSearcher, TermQuery
from org.apache.lucene.search.highlight import QueryTermExtractor
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import BytesRef, BytesRefIterator, Version
from os.path import basename, join, splitext
from sys import stderr

DOCUMENT_FILE_PATTERNS = ["*.html", "*.txt"]
HIGH_FREQUENCY_TERM_THRESHOLD = 0.6
CONTENTS_FIELD_NAME = "contents"
PATH_FIELD_NAME = "path"
FILENAME_FIELD_NAME = "filename"

# Initializes Lucene
def initialize_lucene():
    # print("Starting Lucene Version %s" % lucene.VERSION)
    lucene.initVM()

################################################################################
# Indexing
################################################################################

# Returns an index directory based on path
def get_index_directory(path):
    index_directory = SimpleFSDirectory(File(path).toPath())
    return index_directory

# Returns an index writer based on the given path
def get_index_writer(path):
    index_directory = get_index_directory(path)
    index_writer = IndexWriter(index_directory, IndexWriterConfig())
    return index_writer

# Returns an index reader based on the given path
def get_index_reader(path):
    index_directory = get_index_directory(path)
    index_reader = DirectoryReader.open(index_directory)
    return index_reader

# Indexes the document at `file_name` w/ `index_writer`
def index_file(file_name, index_writer):
    # Create the document
    doc = Document()
    file = File(file_name)
    with open(file_name, "r") as input_file:
        ft = FieldType(TextField.TYPE_NOT_STORED)
        ft.setStoreTermVectors(True)
        doc.add(Field(CONTENTS_FIELD_NAME, input_file.read(), ft))
    doc.add(StringField(PATH_FIELD_NAME, file.getPath(), Field.Store.YES))
    doc.add(StringField(FILENAME_FIELD_NAME, file.getName(), Field.Store.YES))
    
    # Write the document
    index_writer.addDocument(doc)

# Indexes the documents in the given directory to index_path
def index_documents(directory, index_path):
    initialize_lucene()
    index_writer = get_index_writer(index_path)
    for pattern in DOCUMENT_FILE_PATTERNS:
        for file_path in glob(join(directory, pattern)):
            index_file(file_path, index_writer)
    
    # Close the index writer
    print("Wrote %d docs to the index." % index_writer.numDocs())
    index_writer.close()
    
################################################################################
# Querying
################################################################################

# Determines whether a term is a high-frequency term based on its document 
# frequency using the index reader `index_reader`.
def is_not_high_frequency_term(term, index_reader):
    return index_reader.docFreq(Term(CONTENTS_FIELD_NAME, term)) < (HIGH_FREQUENCY_TERM_THRESHOLD * index_reader.numDocs())

# Calculates the Dice Coefficient values based on the simplified index dict 
# structure.
def calculate_dice(index, terms, index_reader):
    dice_values = dict()
    for new_term in list(index.keys()):
        if new_term not in terms and is_not_high_frequency_term(new_term, index_reader):
            dice_values[new_term] = sum([float(len(index[new_term].intersection(index[search_term]))) / float((len(index[new_term]) + len(index[search_term]))) for search_term in terms])
    return dice_values

def select_expanded_terms(index, terms, n, index_reader):
    dice_values = calculate_dice(index, terms, index_reader)
    return [k for k,_ in sorted(dice_values.items(), key=lambda kv: kv[1], reverse=True)[:n]]

def get_query_results(query, result_count, index_searcher):
    return index_searcher.search(query, result_count)

# Return a list of `n` additional terms for `query`.
def get_expanded_terms(query, n, k, index_reader, index_searcher):
    # Perform the query
    expansion_results = get_query_results(query, k, index_searcher)
    
    # Get the terms from the original query
    terms = [t.getTerm() for t in QueryTermExtractor.getTerms(query)]
    
    # Generate a top results index
    top_results_index = defaultdict(set)
    for result in expansion_results.scoreDocs:
        doc = index_searcher.doc(result.doc)
        term_vector = index_reader.getTermVector(result.doc, CONTENTS_FIELD_NAME)
        term_iterator = term_vector.iterator()
        for term in BytesRefIterator.cast_(term_iterator):
            iter = term_iterator.postings(None)
            iter.nextDoc()
            value, freq = term.utf8ToString(), iter.freq()
            # Update frequency in top_results_index
            top_results_index[value].add(result.doc)
    
    return select_expanded_terms(top_results_index, terms, n, index_reader)

# Returns a new query with the terms from `terms` added to `query`.
def add_terms_to_query(query, terms):
    # Create a boolean query builder with the original query
    bc_builder = BooleanQuery.Builder()
    bc_builder.add(query, BooleanClause.Occur.SHOULD)
    
    # Add term queries for the new terms
    for term_text in terms:
        term = Term(CONTENTS_FIELD_NAME, term_text)
        term_query = TermQuery(term)
        bc_builder.add(term_query, BooleanClause.Occur.SHOULD)
    
    return bc_builder.build()

# Expand the query `query` by considering the top `k` ranked documents
# and selecting `n` expansion terms.
def get_expanded_query(query, k, n, index_reader, index_searcher):
    # Generate the boolean query
    expanded_terms = get_expanded_terms(query, n, k, index_reader, index_searcher)
    print("Expanding Query (via PSF) w/ Terms: %s" % ", ".join(expanded_terms), file=stderr)
    
    return add_terms_to_query(query, expanded_terms)

def get_word2vec_expanded_query(query, index_reader):
    # Get the terms from the original query
    terms = [t.getTerm() for t in QueryTermExtractor.getTerms(query)]
    
    # Perform word-embedding query expansion
    model_loaded = Word2Vec.load('dblp_cbow_100.bin') #TODO
    new_terms = []
    for og_term in terms:
        if og_term in model_loaded.wv.vocab:
            similar = [term for term, dist in model_loaded.wv.most_similar(positive=og_term.lower(), topn=3) if dist > 0.6 and is_not_high_frequency_term(term, index_reader)]
            new_terms.extend(similar)
    
    print("Expanding Query (via Word2Vec) w/ Terms: %s" % ", ".join(new_terms), file=stderr)
    
    return add_terms_to_query(query, new_terms)
    
# Perform the query in `query_string` by reading from the index at `index_path` 
# and return `result_count` results. 
# If the given value `k` is greater than 0, then query expansion will be 
# performed based on the top `k` ranked documents from the original query.
# This will expand the query by `n` terms, if possible.
# Note that the number of terms in a query cannot be expanded beyond the 
# default Lucene BooleanQuery getMaxClauseCount() value of 1024.
def perform_query(reader, searcher, query_string, index_path, result_count=100, k=10, n=8, word_vectors_path=None):
    analyzer = StandardAnalyzer()
    
    # Create the initial query based on the provided `query_string`.
    query = SimpleQueryParser(analyzer, CONTENTS_FIELD_NAME).parse(query_string)
    
    # If k (number of ranked documents to use for query expansion) is greater than zero,
    # update the query based on psuedo-relevance feedback
    
    if word_vectors_path is not None:
        query = get_word2vec_expanded_query(query, reader)
    else:
        if k > 0:
            query = get_expanded_query(query, k, n, reader, searcher)
    
    # Generate Results
    results = get_query_results(query, result_count, searcher)
    
    # Print and return results
    # print("Found %s Results. Printing Top %s" % (results.totalHits, result_count))
    # print("\n".join([searcher.doc(result.doc).get(FILENAME_FIELD_NAME) for result in results.scoreDocs]))
    return results.scoreDocs

def process_query_file(index_path, query_file_path, num_results=100, k=10, n=8, word_vectors_path=None):
    initialize_lucene()
    
    reader = get_index_reader(index_path)
    searcher = IndexSearcher(reader)
    
    with open(query_file_path) as query_file:
        qfile_reader = csv_reader(query_file, delimiter='\t')
        for query_row in qfile_reader:
            query_id = query_row[0]
            query_string = query_row[1]
            
            # Get and print 
            results = perform_query(reader, searcher, query_string, index_path, num_results, k, n, word_vectors_path)
            lines = ["%s Q0 %s %s %s Lucene" % (query_id, splitext(basename(searcher.doc(result.doc).get(FILENAME_FIELD_NAME)))[0], idx+1, result.score) for idx, result in enumerate(results)]
            print("\n".join(lines))
