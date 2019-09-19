from lib.shared_utils.stopping import remove_stop_words

from re import sub
from xml.dom import minidom

def convert_query_file(input_path, output_path, stopwords_path, tokenize=True, foldcase=True, handlePunctuation=True):
    
    with open(output_path, "w") as output_file:
        query_doc = minidom.parse(input_path)
        queries = query_doc.getElementsByTagName("DOC")
        for query in queries:
            query_id = query.getElementsByTagName("DOCNO")[0].firstChild.data
            query_text = query.lastChild.data
            
            # Perform stopping
            if stopwords_path is not None:
                stopwords = [stopword.rstrip('\n') for stopword in open(stopwords_path)]
                query_text = remove_stop_words(query_text, stopwords)
            
            # Perform case folding
            if foldcase:
                query_text = query_text.lower()
            
            # Perform punctuation handling, retain only alphanumeric characters
            if handlePunctuation:
                query_text = sub('[^0-9a-zA-Z-]+', ' ', query_text)
            
            # Tokenize
            if tokenize:
                query_text = ' '.join(query_text.split())
            
            output_file.write("%s\t%s\n" % (query_id, query_text))
