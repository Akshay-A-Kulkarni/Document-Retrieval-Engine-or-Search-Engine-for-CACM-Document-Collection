from .indexer import indexes, term_counts as doc_lengths
from .spell_corrector import SpellCorrector
from lib.shared_utils.summarizer import get_text_from_file, summarize

from collections import Counter, defaultdict
from csv import reader as csv_reader
from functools import partial, reduce
from math import log, sqrt
from os.path import join
from re import sub
from statistics import mean
from itertools import chain
import copy
import re
import numpy as np
import numba as nm

index = indexes[0]
mean_doc_length = mean(doc_lengths.values())

# Returns a list of documents containing the term
def docs_containing(term):
	return [doc for doc, count in index.copy()[term].items() if count > 0]

def _get_terms(query_string):
	clean_string = query_string

	# Perform case folding
	clean_string = clean_string.lower()

	# Perform punctuation handling, retain only alphanumeric characters
	clean_string = sub('[^0-9a-zA-Z-]+', ' ', clean_string)

	# Tokenize
	return clean_string.split()

# A simple class representing a BM25 retrieval model
class BM25RetrievalModel:

	# Instance variables for model parameters k1, b, and k2
	def __init__(self):
		self.k1 = float(1.2)
		self.b = float(0.75)
		self.k2 = float(100)
		self.spell_corrector = SpellCorrector(index)

	def K(self, doc_id):
		return self.k1 * ((1 - self.b) + self.b * (doc_lengths[doc_id] / mean_doc_length))

	def idf(self, query_term):
		ni = len(index[query_term])
		N = len(doc_lengths)
		return log(1.0 / ((ni + 0.5) / (N - ni + 0.5)))

	# Returns the ranked value for a query term (`query_term`) and document
	# id (`doc_id`)
	def term_ranked_value(self, query_term, doc_id, query_term_count=1):
		idf_value = self.idf(query_term)
		# Perform copy here to prevent updating value
		fi = index[query_term].copy()[doc_id] # frequency of term i in the document
		doc_value = ((self.k1 + 1) * fi) / (self.K(doc_id) + fi)
		qfi = query_term_count # frequency of term in in the query
		query_value = ((self.k2 + 1) * qfi) / (self.k2 + qfi)
		return idf_value * doc_value * query_value

	# Returns the overall ranked value, summed over a set of query terms
	def overall_ranked_value(self, query_terms, doc_id):
		# Return the actual value, handling duplciate terms with a counter
		return sum([self.term_ranked_value(term, doc_id, query_term_count=count) for term, count in Counter(query_terms).items()])

	# Returns a sorted list of ranked documents based on a list of query terms
	def ranked_documents(self, query_terms):
		# Find matching documents
		matches = set()
		for term in query_terms:
			matches.update(set(docs_containing(term)))

		# Get the ranks of all documents
		ranks = dict()
		for doc_id in sorted(list(matches), reverse=True):
			ranks[doc_id] = self.overall_ranked_value(query_terms, doc_id)

		# Return sorted list
		return sorted(ranks.items(), key=lambda x: x[1], reverse=True)

	# Displays the results for the documents based on the query terms
	def display_documents(self, query_string, docs_path, docs_ext, num_results=None):
		# Get terms
		query_terms = _get_terms(query_string)

		# Get documents
		docs = self.ranked_documents(query_terms)
		if num_results is not None:
			docs = docs[:num_results]

		# Print suggestions
		self.spell_corrector.print_suggestions(query_terms)

		# Print documents and summaries
		for doc, score in docs:
			print("\n" + doc)
			print(summarize(get_text_from_file(join(docs_path, doc + docs_ext)), query_terms, limit=2))

		print('-' * 80)

	# Processes the query file at the given path
	def process_query_file(self, query_file_path, num_results=None):
		with open(query_file_path) as query_file:
			reader = csv_reader(query_file, delimiter='\t')
			for query_row in reader:
				query_id = query_row[0]
				query_terms = _get_terms(query_row[1])
				docs = self.ranked_documents(query_terms)
				if num_results is not None:
					docs = docs[:num_results]
				lines = ["%s Q0 %s %s %s BM25" % (query_id, doc_id, idx+1, score) for idx, (doc_id, score) in enumerate(docs)]
				print("\n".join(lines))

# A simple class representing a query liklihood retrieval model w/ JM (Laplace)
# smoothing.
class QueryLikelihoodModel:
	def __init__(self):
		# Create unigram models for each element in the index
		self.models = defaultdict(partial(defaultdict, int))
		self.collection_lang_model = defaultdict(int)
		self.collection_len = 0
		self.load_language_models_from_index()

	def load_language_models_from_index(self):
		self.collection_lang_model = defaultdict(int)
		self.collection_len = 0
		for term, inner in index.items():
			for doc_id, count in inner.items():
				self.models[doc_id][term] = count
				self.collection_lang_model[term] += count
				self.collection_len += count

	def term_ranked_value(self, query_term, doc_id):
		return 0

	# Returns the overall ranked value, summed over a set of query terms
	def overall_ranked_value(self, query_terms, doc_id):
		# Return the actual value, handling duplciate terms with a counter
		return sum([self.term_ranked_value(term, doc_id) for term in query_terms])

	# Returns a sorted list of ranked documents based on a list of query terms
	def ranked_documents(self, query_terms):
		# Find matching documents
		matches = set()
		for term in query_terms:
			matches.update(set(docs_containing(term)))

		# Get the ranks of all documents
		ranks = dict()
		for doc_id in sorted(list(matches), reverse=True):
			ranks[doc_id] = self.overall_ranked_value(query_terms, doc_id)

		# Return sorted list
		return sorted(ranks.items(), key=lambda x: x[1], reverse=True)

	# Processes the query file at the given path
	def process_query_file(self, query_file_path, num_results=None):
		with open(query_file_path) as query_file:
			reader = csv_reader(query_file, delimiter='\t')
			for query_row in reader:
				query_id = query_row[0]
				query_terms = _get_terms(query_row[1])
				docs = self.ranked_documents(query_terms)
				if num_results is not None:
					docs = docs[:num_results]
				lines = ["%s Q0 %s %s %s QLM" % (query_id, doc_id, idx+1, score) for idx, (doc_id, score) in enumerate(docs)]
				print("\n".join(lines))

class JMQueryLikelihoodModel(QueryLikelihoodModel):

	def __init__(self, λ):
		super().__init__()
		self.λ = λ

	def term_ranked_value(self, query_term, doc_id):
		p_qi_D = self.models[doc_id][query_term] / len(self.models[doc_id])
		pi_qi_collection = self.collection_lang_model[query_term] / self.collection_len
		return log((1 - self.λ) * p_qi_D + self.λ * pi_qi_collection) if pi_qi_collection > 0 else 0.0

class DirichletQueryLikelihoodModel(QueryLikelihoodModel):

	def __init__(self, μ):
			super().__init__()
			self.μ = μ

	def term_ranked_value(self, query_term, doc_id):
		f_qi_D = self.models[doc_id][query_term]
		pi_qi_collection = self.collection_lang_model[query_term] / self.collection_len
		numerator = f_qi_D + self.μ * (pi_qi_collection)
		denominator = len(self.models[doc_id]) + self.μ
		return float(numerator) / float(denominator)



terms = doc_lengths

class VectorSpaceRetrievalModel:

	def __init__(self):
		self.temp = copy.deepcopy(index)
		self.N = len(terms)

	# @nm.jit(nopython=True)
	def computeIDF(self, term):
		if len(index[term].keys()) != 0:
			return log(self.N / len(index[term].keys()))
		else:
			return 0

	def createWMatrix(self, query):
		tf_matrix = defaultdict(dict)
		matches = set()
		for term in query:
			matches.update(set(docs_containing(term)))
		for doc in matches:
			for term in self.temp.keys():
				tf_matrix[doc][term] = self.temp[term][doc]
		return self.computeCosineWeight(tf_matrix)


	def computeCosineWeight(self, fmatrix):
		for doc in fmatrix.keys():
			tsum = 0
			term_dict = {}
			for term, f in fmatrix[doc].items():
				if f == 0:
					tf = 0
				else:
					tf = (log(f) + 1)
				idf = self.computeIDF(term)
				term_dict[term] = tf * idf
				tsum += ((tf * idf) ** 2)
			sqsum = sqrt(tsum)

			for (t, k) in term_dict.items():
				term_dict[t] = k / sqsum
			fmatrix[doc] = term_dict
		return fmatrix
	# Given that the cosine measure normalization is incorporated into the weights, the score for a document is computed
	# using simply the dot product of the document and query vectors
	def createQVec(self, query):
		q_vec = defaultdict(dict)
		q_vec["Query"] = defaultdict(float)
		for k in index.keys():
			for w in query:
				if w == k:
					q_vec["Query"][k] = 1
					break
				else:
					q_vec["Query"][k] = 0
		return self.computeCosineWeight(q_vec)

	def rocchioVec(self, rel_file_path, query_vec, query_id, dvec):
		with open(rel_file_path, "r", encoding='utf-8') as rel_file:
			data = [line.strip() for line in rel_file]
		rel_id = list(chain(*[re.findall("^\d*", s) for s in data]))
		rel_docids = list(chain(*[re.findall("\w+-\w+", s) for s in data]))
		rel_list = list(zip(rel_id, rel_docids))  # zipping them into tuples of (id, docid) for rel reference.
		r_vec = defaultdict(partial(defaultdict, int))
		reldocs = [f for i, f in rel_list if i == str(int(query_id))]
		nonreldocs = list(set(dvec.keys()) - set(reldocs))
		if len(reldocs) != 0 and len(nonreldocs) != 0:
			for k, qw in query_vec["Query"].items():
				rel_sum = 0
				nonrel_sum = 0
				for doc in reldocs:
					rel_sum += dvec[doc][k]
				for doc in nonreldocs:
					nonrel_sum += dvec[doc][k]
				alphaval = 8
				betaval = 16
				gammaval = 4
				r_vec["Query"][k] = alphaval * qw + betaval * (rel_sum / len(reldocs)) + gammaval * (
							nonrel_sum / len(nonreldocs))
		return (r_vec)


	def process_query_file(self, query_file_path, rel_file_path=None, num_results=None):
		with open(query_file_path) as query_file:
			reader = csv_reader(query_file, delimiter='\t')
			for query_row in reader:
				query_id = query_row[0]
				input_query = query_row[1]
				query_vec = self.createQVec(input_query)
				print("Created Query vector")
				dvec_matrix = self.createWMatrix(input_query)
				print("Created Doc Vector")

				# Compute Rocchio Vector if a relevance file is provided
				if rel_file_path is not None:
					query_vec = self.rocchioVec(rel_file_path, query_vec, query_id,
												dvec_matrix)  # computing modified optimal query vector
				# using Rocchio's Algorithm.
				for doc in dvec_matrix:
					rank = [(dvec_matrix[doc][key]) * (query_vec["Query"].get(key)) for key in dvec_matrix[doc]]
					dvec_matrix[doc] = sum(rank)
				if num_results is not None:
					docs = Counter(dvec_matrix)  # using collections.Counter for efficient sorting and using most_common()
					lines = ["%s Q0 %s %s %s VectorSpace" % (query_id, doc_id, idx + 1, score) for idx, (doc_id, score)
							 in
							 enumerate(docs.most_common(num_results))]
					print("\n".join(lines))
