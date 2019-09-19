from os.path import basename
from re import match

def cacm_file_number(filename):
    num_match = match(r".*-(\d+)\.(?:txt|html)", basename(filename))
    doc_num = int(num_match.group(1)) if num_match else None
    return doc_num

#print(cacm_file_number('cacm-000123.txt'))
#print(cacm_file_number('cacm-000123.html'))