from argparse import ArgumentParser
from gensim.models import Word2Vec
from lxml import etree
from re import sub

import numpy as np
import pandas as pd

# This script was used to create word embeddings from document titles with the
# dblp XML file downloaded from 
# https://dblp.uni-trier.de/faq/How+can+I+download+the+whole+dblp+dataset . 
# The number of document titles to use is set by the `-n` parameter. The file 
# included with this submission uses 3,000,000 document titles.
# Any document titles containing special, undefined characters will be skipped, 
# unless those are defined at the top of the XML file.
parser = ArgumentParser(description='Creates word embeddings from the dblp XML file.')
parser.add_argument("filepath", help="the path to the dblp XML file")
parser.add_argument("title_count", help="the number of titles to read from the XML file", type=int)

args = parser.parse_args()

def tokenize_document_title(doc_title):
    title = doc_title
    title = sub('[^0-9a-zA-Z-]+', ' ', title)
    return title.lower().split()

def read_document_titles(file, to_read=3000000):
    document_titles = []
    context = etree.iterparse(file, recover=True)
    context = iter(context)
    event, root = context.__next__()
    doc_count = 0
    for event, elem in context:
        # Add the title to the list
        if event == "end" and elem.tag == "title":
            title = str(elem.text)
            document_titles.append(title)
            
            # Update document count, exit after reaching
            doc_count += 1
            if doc_count >= to_read:
                break
        
        # Get rid of elements to save memory
        root.clear()
    return pd.Series(document_titles).apply(tokenize_document_title)

print("Reading Document Titles...")
doc_titles = read_document_titles(args.filepath, to_read=args.titlecount)
print("Read %s Document Titles" % (doc_titles.size,))

print("Creating Word2Vec Model (CBOW)...")
model = Word2Vec(doc_titles, sg=0, size=100, window=10, min_count=5, workers=8)
print("Training Word2Vec Model...")
model.train(doc_titles, total_examples=len(doc_titles), epochs=10)
print("Writing Word2Vec Model...")
model.save('dblp_cbow_100.bin')
print("Done.")