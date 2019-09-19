from collections import defaultdict
from copy import deepcopy
from re import sub

class SpellCorrector:
    
    # These are the 'in-game' characters for spelling correction
    change_chars = 'abcdefghijklmnopqrstuvwxyz123456789'

    def __init__(self, unigram_index):
        # Language model: term (str) -> count (int)
        self.unigram_index = deepcopy(unigram_index)
        self.term_count = sum([sum(inner_dict.values()) for inner_dict in self.unigram_index.values()])
    
    # Returns the base probability of a given term
    def p(self, word):
        return float(sum(self.unigram_index[word].values())) / float(self.term_count)
    
    # Prints the suggestions for the provided terms.
    def print_suggestions(self, terms):
        for term in terms:
            sug_text = self._suggestion_text(term)
            if sug_text is not None:
                print("\n" + sug_text)
    
    # Returns all possible corrections based on an edit-distance of two. Ranked 
    # by unigram probability of occurance.
    def suggestions(self, word):
        # Because we used the set `or` operator, usimg the sorted function here 
        # will automatically list words within 1 edit distance away if 
        # possible. Otherwise, it will backoff to an edit distance of 2.
        # It will stop after an edit distance of two for efficiency.
        return sorted(self.dict_edits(word, distance=1) or self.dict_edits(word, distance=2), key=self.p, reverse=True)
    
    # Provides the suggestion text based on a given query, or None if no 
    # suggestion should be given.
    def _suggestion_text(self, word, limit=6):
        if word.lower() not in self.unigram_index.keys():
            sugs = self.suggestions(word.lower())[:limit]
            if len(sugs) > 0:
                return "The term '%s' was not found. Did you mean?:\n%s" % (word, "\n".join(sugs))
        #else:
            #print("wft 1 |%s| %s" % (word, word in self.unigram_index))
            #print(self.unigram_index[word])
        return None
    
    # Returns a set of all edits within the given edit distance. 
    # Note that this is a recursive function and the list will quickly grow
    # as edit distance increases.
    def edits(self, word, distance=1):
        return set(self._edits(word.lower(), distance=distance))
    
    def _edits(self, word, distance):
        if distance <= 0:
            return []
        else:
            new_edits = self._del_edits(word) + self._insert_edits(word) + self._replace_edits(word) + self._swap_edits(word)
            if distance <= 1:
                return new_edits
            else:
                return new_edits + [edit_2 for edit_1 in new_edits for edit_2 in self._edits(edit_1, distance - 1)]
    
    # Returns the exits currently in the vocabulary
    def dict_edits(self, word, distance=1):
        all_edits = self.edits(word, distance=distance)
        return set(edit for edit in all_edits if edit in self.unigram_index)
    
    # Return all possible deletions
    def _del_edits(self, word):
        return [word[:i] + word[(i+1):] for i in range(0, len(word))]
    
    # Return all possible one character inserts
    def _insert_edits(self, word):
        return [word[:i] + repl_char + word[i:] for i in range(0, len(word)+1) for repl_char in SpellCorrector.change_chars]
    
    # Return all possible one character replacements
    def _replace_edits(self, word):
        return [word[:i] + repl_char + word[i+1:] for i in range(0, len(word)) for repl_char in SpellCorrector.change_chars]
    
    # Return all possible one character swaps
    def _swap_edits(self, word):
        if len(word) > 1:
            return [word[:i] + word[i+1] + word[i] + word[i+2:] for i in range(0, len(word) - 1)]
        else:
            return []

#from pickle import load as pickle_load
#model = SpellCorrector(pickle_load(open('../../index.p', "rb")))
#print(model._del_edits('spelin'))
#print(model._insert_edits('spelin'))
#print(model._replace_edits('spelin'))
#print(model._swap_edits('spelin'))
#print(len(model.edits('spelin', distance=2)))
#print(model.dict_edits('spelin', distance=2))
#print(model.suggestions('spelin'))
#print(model.suggestions('22'))
#print(model.suggestion_text('spelin'))
#print(model.suggestion_text('coursed'))