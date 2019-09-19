from bs4 import BeautifulSoup
from os import listdir, makedirs
from os.path import basename, exists, isfile, join, splitext
from re import sub
from warnings import warn

def process_directory(input_dir, output_dir, tokenize=True, foldcase=True, handlePunctuation=True, removeFinalInts=True):
    for file_or_dir in listdir(input_dir):
        # Note: This will list files and directories. `process_document` will 
        # handle ignoring non-text files.
        if not exists(output_dir):
            makedirs(output_dir)
        process_document(join(input_dir, file_or_dir), output_dir, tokenize=tokenize, foldcase=foldcase, handlePunctuation=handlePunctuation)

def process_document(input_path, output_dir, tokenize=True, foldcase=True, handlePunctuation=True, removeFinalInts=True):
    base = splitext(basename(input_path))[0]
    if base:
        filename = join(output_dir, "%s.txt" % (base,))
        if isfile(filename):
            warn("%s already exists" % filename)
        else:
            with open(input_path, "r") as input_file:
                text = input_file.read()
                
                soup = BeautifulSoup(text, 'html.parser')
                article = soup.text
                
                # Perform case folding
                if foldcase:
                    article = article.lower()
                
                # Perform punctuation handling, retain only alphanumeric characters
                if handlePunctuation:
                    article = sub('[^0-9a-zA-Z-]+', ' ', article)
                
                # Tokenize
                if tokenize:
                    article = ' '.join(article.split())
                
                # Remove integers at end of file
                if removeFinalInts:
                    split_article = article.split()
                    while split_article[-1] is not None and split_article[-1].isdigit():
                        del split_article[-1]
                    article = ' '.join(split_article)
                
                with open(filename, "w") as text_file:
                    text_file.write(article)