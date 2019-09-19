from bs4 import BeautifulSoup
from nltk import download as nltk_download
from nltk.data import find as nltk_find
from nltk.tokenize import sent_tokenize as nltk_sent_tokenize, word_tokenize as word_tokenize
from os.path import splitext
from re import compile, IGNORECASE, split as re_split

# Download English data for tokenizing
try:
    nltk_find('tokenizers/punkt')
except LookupError:
    nltk_download('punkt')

def sent_tokenize(text):
    # return [token for token in re_split('\n\n|\.', text) if len(token) > 0]
    return nltk_sent_tokenize(compile('\n\n+').sub(". ", text.strip()))

# Gets the text from a file at path, either in '.txt' or '.html' format. 
# For other files, returns an empty string.
def get_text_from_file(path):
    with open(path, "r") as input_file:
        text = input_file.read()
        
        clean_text = ""
        if splitext(path)[1].lower() == ".txt":
            # Already have text
            clean_text = text
        elif splitext(path)[1].lower() == ".htm" or splitext(path)[1].lower() == ".html":
            soup = BeautifulSoup(text, 'html.parser')
            clean_text = soup.text
        
        return clean_text

def sent_score(sentence, terms):
    words = word_tokenize(sentence)
    
    # Lowercase both words and sentences
    l_words = [word.lower() for word in words]
    l_terms = [term.lower() for term in terms]
    
    keyword_indexes = [i for i, x in enumerate(l_words) if x in l_terms]
    if len(keyword_indexes) > 0:
        key_phrase_len = 1 + keyword_indexes[-1] - keyword_indexes[0]
        score = float(len(keyword_indexes) ** 2) / key_phrase_len
        return score
    else:
        return 0

def summarize(text, terms, limit=None):
    sents = sent_tokenize(text)
    scores = [sent_score(sent, terms) for sent in sents]
    sent_scores = sorted([(sent, score) for sent, score in zip(sents, scores) if score > 0], key=lambda tup: tup[1], reverse=True)
    
    # Take top sentences based on limit, if applicable
    if limit is not None:
        sent_scores = sent_scores[:limit]
        
    result_text = " ".join([sent for sent, score in sent_scores]) # Join sentences into block.
    result_text = " ".join(result_text.split()) # Clean whitespace.
    return highlight(result_text, terms)

def highlight(text, terms):
    h_text = text
    for term in terms:
        h_text = str(compile(r'(?<!-)\b(%s)(?<!-)\b' % (term), IGNORECASE).sub(r'\033[1m\1\033[0m', h_text))
    return h_text

#text = get_text_from_file('../../cacm/CACM-3182.html')
#print(summarize(text, ['Technological', 'Advances']))
#print(summarize(text, ['FINANCIAL', 'CRIMES']))
#print(summarize(text, ['EFTs'], limit=2))