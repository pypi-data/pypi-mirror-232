import pdfminer 
from pdfminer.high_level import extract_text
import re
import numpy as np

def converts_pdf_to_string(path_to_pdf):
    return extract_text(path_to_pdf)

'''
 - Finds the all the double newline indices '\n\n' (ie where the paragraph breaks are), stores these indices in a list,
loops through these indices and uses these indices to slice the orginal text.
 - Uses list comprehension to remove the remaining '\n' tags.
 - Returns a list of (mostly) cleaned text.
'''
def splits_string_by_newlines(pdf_as_string, is_double_spaced=False):
    paragraph_chunks_ary = []
    
    if is_double_spaced:
        string_without_double_line_break = pdf_as_string.replace('\n\n', '')
        period_idx = [m.start() for m in re.finditer('\.', string_without_double_line_break)]

        # Iterates through all of the '.'s in the string
        for a, b in zip(period_idx, period_idx[4:]):
            # If the character before the '.' lowercase and is the 2nd character after uppercase append the chunk of text to paragraph_chunks_ary.
            if string_without_double_line_break[a-1].islower() and string_without_double_line_break[a+2].isupper():
                paragraph_chunks_ary.append(string_without_double_line_break[a+2:b+1])        

                
    else:
        newline_idx = [m.start() for m in re.finditer('\n\n', pdf_as_string)]
        for a, b in zip(newline_idx, newline_idx[1:]):
            paragraph_chunks_ary.append(pdf_as_string[a+1:b])
    
    paragraph_chunks_ary = [s.replace('\n', '').replace('\x0c', '') for s in paragraph_chunks_ary]
        
    return paragraph_chunks_ary

'''
 Takes a list of strings that are seperated by newlines and returns a list of strings that are further reduced.
 - Splits the blocks of text into smaller sentences by slicing the text blocks by the middle '.' in the text block.
 - Then returns a list of these strings that are as long or longer than the average length of split strings.
    - This helps elminate most of the math equations and any remainer misc headers, footers, captions etc.
'''
def splits_strings_into_sentences(paragraph_chunks_ary):
    tagless_strings_len = []
    split_sentece_ary = []  
    
    # Works but is not space efficient
    for idx, string in enumerate(paragraph_chunks_ary):
        period_finder = [m.start() for m in re.finditer('\.', string)]

        # If there is more than 1 '.' in the text block split the text by the middle '.' and append both sides to split_sentence_ary
        if len(period_finder) > 1:
            middle_idx = period_finder[int((len(period_finder) - 1)/2)]
            split_sentece_ary.append(string[:middle_idx+1])
            split_sentece_ary.append(string[middle_idx+1:])
        else:
            split_sentece_ary.append(string)
            
    # Gets the length of all the strings in the split_sentence_ary
    tagless_strings_len = [len(string) for string in split_sentece_ary]
            
    # Keeps only the strings in the array that are longer that the average length
    split_sentece_ary = [s for s in paragraph_chunks_ary if len(s) >= np.mean(tagless_strings_len)]    
    
    return split_sentece_ary
