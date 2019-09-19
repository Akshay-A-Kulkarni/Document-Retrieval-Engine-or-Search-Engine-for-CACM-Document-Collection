Phase 1, Task 1:
* From Scratch:
    * BM25 (required)
    * TF/IDF
    * Binary Independence Model
* Lucene
    * Default Retrieval Model

Phase 1, Task 2:
* For Lucene Default?
    * Pseudo-Relevance Feedback
        * Select Params
    * Word2vec Word Embedding Query Expansion
        * Use Google News pre-trained word embeddings
        * Number of expansion terms to generate?
            * 3 per initial term that isn’t a stop word?

Phase 1, Task 3:
* For BM25 and TF/IDF?
    * Stopping
    * Stemming

Phase 2:
* Snippet Generation
    * INPUT: document IDs, original (non-expanded) query terms
    * OUTPUT: snippets for each document w/ highlighting 
    * Run on Lucene Default?
    * Method?
        * ???
Phase 3:
* Additional Run: Stopping with Word Embedding Query Expansion
* Perform Evaluation
    * MAP
    * MRR
    * P@K, K = 5 and 20
    * Precision & Recall (provide full tables for all queries and all runs)

Extra Credit:
* Spelling Correction