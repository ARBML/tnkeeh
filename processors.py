import re
import math

# remove diacritics
def remove_tashkeel(text):
    text = re.sub(r"[ًٌٍَََُِّْ]", "", text)
    return text

# normalize data
def normalize_data(text, norm_dict):
    # use a mapping dictionary 
    regex = re.compile("|".join(map(re.escape, norm_dict.keys())))
    text  = regex.sub(lambda match: norm_dict[match.group(0)], text)
    return text 

# remove English characters 
def remove_english_chars(text):
    return re.sub('[a-zA-Z]', '', text)

def remove_digits(text):
    return re.sub('[0-9]', '', text)

def remove_all_english(text):
   return re.sub('[a-zA-Z0-9]', '', text) 

def keep_only_arabic_chars(text):
    text = re.compile('([\n\u0621-\u064A0-9])').sub(r' ', text)
    return text

# https://github.com/google-research/bert/blob/master/tokenization.py
def is_punctuation(char):
    cp = ord(char)
    if cp == 1567:
        return True
    if cp in range(33, 48) or cp in range(58, 65) or cp in range(91, 97) or cp in range(123, 127):
        return True
    else:
        return False 

def remove_extra_spaces(text):
    text = re.sub(" +", " ", text)
    return text

def add_spaces_to_all_nonchars(text):
    # event English
    text = re.compile('([^\n\u0621-\u064A0-9])').sub(r' \1 ', text)
    return text

def save_list(list, file_name)
    open(file_name, 'w').write(('\n').join(list))


