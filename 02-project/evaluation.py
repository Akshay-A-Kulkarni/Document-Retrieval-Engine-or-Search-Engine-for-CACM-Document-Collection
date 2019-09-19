from argparse import ArgumentParser
from collections import defaultdict
from statistics import mean

parser = ArgumentParser(description='Performs evaluation metrics based on a relevance file (assumed to be binary) and a retrieval results file.')
parser.add_argument("relevance_file_path", help="the path to read the trec binary relevance file from")
parser.add_argument("results_file_path", help="the path to read the trec results file from")

args = parser.parse_args()

# FILE MANAGEMENT
################################################################################

# Applies `function` to the split content of each line in the file at `path`.
def _apply_to_split_rows(path, function):
    with open(path, 'r') as infile:
        for line in infile.readlines():
            content = line.split()
            function(content)

def read_binary_relevance_file(path):
    # map of query_id -> set of relevant documents
    relevant_docs = defaultdict(set)
    # c[0] is query_id
    # c[2] is doc_id
    _apply_to_split_rows(path, lambda c: relevant_docs[c[0]].add(c[2]))
    return relevant_docs

def read_result_file(path):
    # map of query_id -> ordered list of relevant documents
    results = defaultdict(list)
    # c[0] is query_id
    # c[2] is doc_id
    _apply_to_split_rows(path, lambda c: results[c[0]].append(c[2]))
    return results

relevance_data = read_binary_relevance_file(args.relevance_file_path)
results_data = read_result_file(args.results_file_path)

# Average Precision
################################################################################

def precision(query_id, k):
    relevant_documents = relevance_data[query_id]
    retrieved_documents = set(results_data[query_id][:k])
    return len(relevant_documents & retrieved_documents) / len(retrieved_documents)

def average_precision(query_id):
    return mean([precision(query_id, k) for k in range(1, len(results_data[query_id]) + 1)])

def print_mean_average_precision():
    print("MEAN AVERAGE PRECISION")
    print("-" * 80)
    print("MAP: ", mean([(average_precision(query_id)) for query_id in relevance_data.keys()]))
    for query_id in relevance_data.keys():
        print("Query %s : %s" % (query_id, average_precision(query_id)))



# Reciprocal Rank
################################################################################

def reciprocal_rank(query_id):
    query_results = results_data[query_id]
    for i in range(0, len(query_results)):
        if query_results[i] in relevance_data[query_id]:
            return 1.0 / float(i + 1)
    return float(0)

def print_mean_reciprocal_rank():
    print("MEAN RECIPROCAL RANK")
    print("-" * 80)
    print("MRR: ", mean([(reciprocal_rank(query_id)) for query_id in relevance_data.keys()]))
    for query_id in relevance_data.keys():
        print("Query %s : %s" % (query_id, reciprocal_rank(query_id)))

# P@K
################################################################################

def print_p_at_k(k_values):
    print("PRECISION AT K")
    print("-" * 80)
    for k in k_values:
        print("Overall @k=%s: " % (k,), mean([(precision(query_id, k)) for query_id in relevance_data.keys()]))
    for query_id in relevance_data.keys():
        for k in k_values:
            print("Query %s (k=%s): %s" % (query_id, k, precision(query_id, k)))

# Precision and Recall
################################################################################

def recall(query_id, k):
    relevant_documents = relevance_data[query_id]
    retrieved_documents = set(results_data[query_id][:k])
    return len(relevant_documents & retrieved_documents) / len(relevant_documents)

def print_precision_and_recall():
    print("PRECISION AND RECALL")
    print("-" * 80)
    print("Overall Precision: ", mean([(precision(query_id, len(results_data[query_id]))) for query_id in relevance_data.keys()]))
    print("Overall Recall: ", mean([(recall(query_id, len(results_data[query_id]))) for query_id in relevance_data.keys()]))
    for query_id in relevance_data.keys():
        print("Query %s : P=%s, R=%s" % (query_id, precision(query_id, len(results_data[query_id])), recall(query_id, len(results_data[query_id]))))

################################################################################

# Print it all...
print_mean_average_precision()
print()
print_mean_reciprocal_rank()
print()
print_p_at_k([5, 20])
print()
print_precision_and_recall()