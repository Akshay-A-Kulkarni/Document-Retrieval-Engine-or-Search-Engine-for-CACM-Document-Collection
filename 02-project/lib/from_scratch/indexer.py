from collections import defaultdict
from csv import writer as csvwriter
from functools import partial
from glob import glob
from nltk import ngrams
from os.path import basename, join, splitext
from pickle import load as pickle_load, dump as pickle_dump

INDEX_FILE_PATTERN = "*.txt"
MAX_N = 3

# Index: maps term -> docID -> count
indexes = [defaultdict(partial(defaultdict, int)) for i in range(MAX_N)]

# TermCounts: maps docID to term count
term_counts = defaultdict(int)

# PositionalIndex: term -> docID -> positions
positional_index = defaultdict(partial(defaultdict, list))

def read_tokenized_document(path):
	with open(path, "r") as text_file:
		return text_file.read().split()

def index_document(path):
	docID = splitext(basename(path))[0]
	doc = read_tokenized_document(path)
	
	# Update index for n-grams
	for n in range(MAX_N):
		terms = doc if n == 0 else ngrams(doc, n + 1)
		for term in terms:
			indexes[n][term][docID] += 1
	# Per Piazza: You need to count the number of terms in each document, not necessarily unique.
	term_counts[docID] = len(doc)
	#term_counts[docID] = len(set(doc)) # Update term counts, if unique
		
	# Update positional index
	for (i, term) in enumerate(doc):
		position_list = positional_index[term][docID]
		position_list.append(i - sum(position_list))
		positional_index[term][docID] = position_list

def index_documents(directory):
	for file_path in glob(join(directory, INDEX_FILE_PATTERN)):
		index_document(file_path)

# Writes the index for the specified `n`-gram value to `output_path`.
def write_index(output_path, n=1):
	with open(output_path, "wb") as output_file:
		pickle_dump(indexes[n-1], output_file)

# Reads the index for the specified `n`-gram value from `input_path`.
def read_index(input_path, n=1):
	global indexes
	with open(input_path, "rb") as input_file:
		indexes[n-1] = pickle_load(input_file)

# Writes the term counts data structure to `output_path`.
# Writes in a format that can be read in later by the application, unless the 
# `human_readable` option is specified.
def write_term_counts(output_path, human_readable=False):
	if human_readable:
		with open(output_path, "w") as output_file:
			csv_output = csvwriter(output_file)
			csv_output.writerow(['docID', 'term count'])
			for row in term_counts.items():
				csv_output.writerow(row)
	else:
		with open(output_path, "wb") as output_file:
			pickle_dump(term_counts, output_file)

# Reads the term counts file, when in the non-human readable format, from 
# `input_path`.
def read_term_counts(input_path):
	global term_counts
	with open(input_path, "rb") as input_file:
		term_counts = pickle_load(input_file)

# Writes the positional index to `output_path`.
def write_positional_index(output_path):
	with open(output_path, "wb") as output_file:
		pickle_dump(positional_index, output_file)

# Reads a positional index file from `input_path`.
def read_positional_index(input_path):
	global positional_index
	with open(input_path, "rb") as input_file:
		positional_index = pickle_load(input_file)

def list_from_d_gaps(d_gaps):
	result = []
	current_sum = 0
	for gap in d_gaps:
		current_sum += gap
		result.append(current_sum)
	return result

# Performs a conjunctive proximity query based on the loaded index, based on 
# the terms `t1` and `t2`, and the proximity window `k`.
def perform_conjunctive_proximity_query(t1, t2, k):
	t1_posting = positional_index[t1.lower()]
	t2_posting = positional_index[t2.lower()]
	
	docIDs = set(t1_posting.keys()).intersection(set(t2_posting.keys()))
	
	def within_k(t1_positions, t2_positions, k):
		t1_i = 0
		t2_i = 0
		
		while t1_i < len(t1_positions) and t2_i < len(t2_positions):
			if abs(t1_positions[t1_i] - t2_positions[t2_i]) <= k:
				return True
			else:
				if t1_positions[t1_i] < t2_positions[t2_i]:
					t1_i += 1
				else:
					t2_i += 1
					
		return False
	
	docIDs = set(filter(lambda docID: within_k(list_from_d_gaps(t1_posting[docID]), list_from_d_gaps(t2_posting[docID]), k), docIDs))
	
	print("\n".join(docIDs))
	print("===============\n%s Documents Found" % (len(docIDs),))

def term_frequency_table(index):
	term_counts = [(term, sum(docCounts.values())) for term, docCounts in index.items()]
	return sorted(term_counts, key=lambda kv: kv[1], reverse=True)

# Writes the term frequency table for the specified index to `output_path`.
def write_term_fequency_table(index, output_path):
	with open(output_path, "w") as output_file:
		csv_output = csvwriter(output_file)
		csv_output.writerow(['term', 'term frequency'])
		for row in term_frequency_table(index):
			csv_output.writerow(row)

def document_frequency_table(index):
	counts = [(term, " ".join(docCounts.keys()), len(docCounts.values())) for term, docCounts in index.items()]
	return sorted(counts, key=lambda tup: tup[0])

# Writes the document frequency table for the specified index to `output_path`.
def write_document_fequency_table(index, output_path):
	with open(output_path, "w") as output_file:
		csv_output = csvwriter(output_file)
		csv_output.writerow(['term', 'docIDs', 'document frequency'])
		for row in document_frequency_table(index):
			csv_output.writerow(row)