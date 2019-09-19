This file provides documentation for the Final Project for CS 6200. 
Submitted by Brian Desnoyers, John Goodacre, and Akshay Kulkarni.

The script for this assignment is written in Python 3. Since PyLucene is 
difficult to support and provide cross-platform install instructions for, it 
has been set up as a Docker image which will automatically copy over the 
assignment code. 

Note that if you already have PyLucene installed, you can simply create a 
Python 3 virtual enviroment, install the requirements in `Requirements.txt` via 
`pip`, add PyLucene to the enviroment, and run. However, the Docker set-up 
here will automate that process.

The third-party libraries used are listed in `Requirements.txt` in addition to 
the PyLucene base image (coady/pylucene).

This uses version 7.7.1 of Lucene.

To run the code:

    1.  Ensure Docker is installed, configured, and running.
    2.  Move into the unzipped `Brian_Desnoyers_HW5` directory (i.e. use cd).
    3.  Build the Docker image. This will require an internet connection to 
        download PyLucene and install the requirments in `Requirements.txt` via 
        PyPI.
            ```
            docker build -t ir_project_image .
            ```
    4.  Run Bash shell in the Docker container from the image, giving the 
        container the name `desnoyers_ir_asn4_cont`.
            ```
            docker run -i -t --rm --name ir_project_cont ir_project_image /bin/bash
            ```
    5.  As part of this Docker-ized set-up the required documents and query 
        files are automatically copied into the container. 
        Additional files can be copied into the folder `/usr/src` within the 
        container.
        Note that this will not work if the container is not running (see step 
        4). This will need to be run within the host system shell, not the 
        Docker container's shell.
            ```
            docker cp new_query_file.tsv ir_project_cont:/usr/src/
            ```
    6.  You can then run the scripts for each part of the assignment from the 
        Bash shell for the Docker container. 
    
================================================================================
General
================================================================================

For all main source documents in the root directory, argument documentation is 
provided via the `--help` argument:
    ```
    python [script_name].py --help
    ```

All commands used to complete the project are detailed below.

Case fold and clean non-alphanumeric characters from the CACM collection. 
    ```
    python preprocess_cacm.py cacm cacm-clean
    ```

Generate a "from scratch" index from the cleaned CACM collection.
    ```
    python index_scratch.py cacm-clean --uni index.p --termcounts termcounts.p
    ```

Generate a Lucene index from the un-cleaned CACM collection.
    ```
    python index_lucene.py cacm lucene_index 
    ```

Convert the XML query file into a TSV file for use with the query systems. 
Note: the provided XML query file is actually not valid XML since it was 
missing a root. That has been added to the version submitted here.
    ```
    python convert_query_file.py  test-collection/cacm.query.txt clean_queries.tsv
    python convert_query_file.py  test-collection/cacm.query.txt unclean_queries.tsv --preventclean
    ```

================================================================================
Phase 1
================================================================================

Task 1 Runs:

Perform the baseline run for the "from scratch" Jelinek-Mercer smoothed Query 
Likelihood Model retrieval system, using a lambda value of 0.7. This value was 
selected due to the longer queries in the dataset.
    ```
    python baseline_qlm_JM-smoothed.py index.p termcounts.p clean_queries.tsv -l 0.7 -r 100 > results_baseline_qlm_JM-smoothed.txt
    ```

Just for fun, a Dirichlet smoothed Query Likelihood Model retrieval system was 
also implemented and queried using a mu value of 1000. This value was selected 
due to the longer queries in the dataset.
    ```
    python baseline_qlm_Dirichlet-smoothed.py index.p termcounts.p clean_queries.tsv -l 1000 -r 100 > results_baseline_qlm_Dirichlet-smoothed.txt
    ```

Perform the baseline run for the "from scratch" BM25 retrieval system.
    ```
    python baseline_BM25.py index.p termcounts.p clean_queries.tsv -r 100 > results_baseline_bm25.txt
    ```

Perform the baseline run for the default Lucene retrieval system.
    ```
    python baseline_lucene.py lucene_index unclean_queries.tsv -r 100 > results_baseline_lucene.txt
    ```

Bonus Run: We also implemented a vector space model in addition to the required ones.
Note: This one takes about an hour to run and is an area for improvement.
Perform the baseline run for the "from scratch" tf-idf vector space retrieval 
system. 
    ```
    python baseline_VectorSpace_Tf_Idf.py index.p termcounts.p clean_queries.tsv -r 100 > results_baseline_VectorSpace.txt
    ```
This can utilize relevance information using Rocchio's Algorithm for the same 
set of queries if that is provided via the `-rel` argument.
    ```
    python baseline_VectorSpace_Tf_Idf.py index.p termcounts.p clean_queries.tsv -rel test-collection/cacm.rel.txt -r 100 > results_baseline_VectorSpace_With_Rocchio_Optimum_Query_.txt
    ```

Task 2 Runs:

Perform the baseline run for the default Lucene retrieval system using pseudo-
relevance feedback.
    ```
    python baseline_lucene.py lucene_index unclean_queries.tsv -r 100 -k 10 -n 8 > results_pseudo_lucene.txt
    ```

Perform the baseline run for the default Lucene retrieval system using word 
embedding-based query expansion. 
    ```
    python baseline_lucene.py lucene_index unclean_queries.tsv -r 100 -w dblp_cbow_100.bin > results_word2vec_lucene.txt
    ```
(The example command above uses the trained word embeddings included with this 
submission, which were trained on 3,000,000 article titles from the dblp 
dataset. Since the training of the model is not necessary for the run and thus 
out of the scope of this document, it won't be detailed in this file. The 
script used to generate the embeddings includes documentation and is included 
in `create_embeddings.py`.)
    
Task 3 Runs:

To generate a stopped version of the query files, the `--stopwords` parameter 
was passed to the `convert_query_file.py` as shown below.
    ```
    python convert_query_file.py test-collection/cacm.query.txt clean_stopped_queries.tsv --stopwords test-collection/common_words
    python convert_query_file.py test-collection/cacm.query.txt unclean_stopped_queries.tsv --preventclean --stopwords test-collection/common_words
    ```

The baseline stopped runs were then performed using the baseline Lucene model 
and the BM25 model, as shown below.
    ```
    python baseline_lucene.py lucene_index unclean_stopped_queries.tsv -r 100 > results_stop_lucene.txt
    python baseline_BM25.py index.p termcounts.p clean_stopped_queries.tsv -r 100 > results_stop_bm25.txt
    ```

For stemming, the stemmed documents were extracted to the directory `cacm-stem` 
using `extract_stemmed_documents.py` as shown below.
    ```
    python extract_stemmed_documents.py test-collection/cacm_stem.txt cacm-stem
    ```
Generate a "from scratch" index from the stemmed CACM collection.
    ```
    python index_scratch.py cacm-stem --uni stem_index.p --termcounts stem_termcounts.p
    ```
Generate a Lucene index from the stemmed CACM collection.
    ```
    python index_lucene.py cacm-stem stem_lucene_index
    ```
Add query IDs to the stemmed query file so that we can tell queries apart.
    ```
    awk '{print NR, "\t", $0}' test-collection/cacm_stem.query.txt > stem_queries.tsv
    ```


The baseline stemmed runs were then performed using the baseline Lucene model 
and the vector space model, as shown below.
    ```
    python baseline_lucene.py stem_lucene_index stem_queries.tsv -r 100 > results_stem_lucene.txt
    python baseline_BM25.py stem_index.p stem_termcounts.p stem_queries.tsv -r 100 > results_stem_bm25.txt
    ```

================================================================================
Phase 2 (Displaying Results)
================================================================================

Snippet generation and query term highlighting have been implemented for the 
BM25 baseline run. To perform a single query and display results, a separate 
wrapper script has been created.

The example command below was used to retrieve and display results for the 
query 'boolean retrieval model' and access documents based on their docIDs 
within the `cacm` directory, while appending the `.html` extension.
    ```
    python baseline_BM25_text-query.py index.p termcounts.p "boolean retrieval model" cacm .html -r 100
    ```

An entire run was displayed using the `baseline_BM25_file-query.py` script as 
shown below (shorted to 5 results for each query).
    ```
    python baseline_BM25_file-query.py index.p termcounts.p clean_queries.tsv cacm .html -r 5
    ```

Note: the bold text characters used for highlighting require a VT100-compatible 
terminal, or you will see extra characters in place of highlighting.

================================================================================
Phase 3 (Evaluation)
================================================================================

A final run was performed to combine the word embedding-based query expansion 
with stopping for the Lucene retrieval model, as shown below.
    ```
    python baseline_lucene.py lucene_index unclean_stopped_queries.tsv -r 100 -w dblp_cbow_100.bin > results_stopped_word2vec_lucene.txt
    ```

The source code for performing the evaluation is included in `evaluation.py`. 

Argument documentation is provided via the command:
    ```
    python evaluation.py --help
    ```

The command below was used to evaluate results from the BM25 baseline query. 
This process was repeated for all of the results files in a similar pattern and 
are included with this submission as `eval_*.txt`.
    ```
    python evaluation.py test-collection/cacm.rel.txt results_baseline_bm25.txt > eval_baseline_bm25.txt
    ```

================================================================================
Extra Credit (Spelling Correction)
================================================================================

For extra credit, a simple unigram model-based on an edit distance of 1 or 2 
was created. This has been integrated into the query interface used to display 
results. 

For example, when mispelling the same query used before with the query 
interface, up to six spelling suggestions will be provided for each term not in 
the index.
```
python baseline_BM25_text-query.py index.p termcounts.p "bolean retrieval model" cacm .html -r 100
```