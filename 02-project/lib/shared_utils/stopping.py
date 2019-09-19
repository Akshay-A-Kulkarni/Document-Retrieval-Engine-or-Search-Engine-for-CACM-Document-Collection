from re import sub, IGNORECASE

def remove_stop_words(string, stop_words):
    result = string
    for sw in stop_words:
        result = sub(r'(?<!-)\b' + sw + r'(?!-)\b', '', result, flags=IGNORECASE)
    return result