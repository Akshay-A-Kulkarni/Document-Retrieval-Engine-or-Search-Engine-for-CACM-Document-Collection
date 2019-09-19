FROM coady/pylucene:7.7.1

# Copy library code
COPY lib/ ./lib/

# Copy setup scrupts
COPY preprocess_cacm.py ./
COPY convert_query_file.py ./
COPY extract_stemmed_documents.py ./

# Copy indexing scripts
COPY index_scratch.py ./
COPY index_lucene.py ./

# Copy baseline scripts
COPY baseline_BM25.py ./
COPY baseline_BM25_file-query.py ./
COPY baseline_BM25_text-query.py ./
COPY baseline_lucene.py ./
COPY baseline_qlm_JM-smoothed.py ./
COPY baseline_qlm_Dirichlet-smoothed.py ./
COPY baseline_VectorSpace_Tf_Idf.py ./

# Copy test collection
COPY cacm/ ./cacm/
COPY test-collection/ ./test-collection/

# Copy Word Embeddings
COPY dblp_cbow_100.bin ./

# Copy evaluation script
COPY evaluation.py ./

# Copy requirements file and install via pip
COPY Requirements.txt ./
RUN pip install -r Requirements.txt