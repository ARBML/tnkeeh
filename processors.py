import re
import math
from farasa.segmenter import FarasaSegmenter
import sys
import os
# remove diacritics
def remove_tashkeel(text):
    text = re.sub(r"[ًٌٍَََُِّْ]", "", text)
    return text

# normalize data
def normalize_data(text):
    norm_dict = pickle.load(open(norm_dict_path, "rb"))
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
def get_all_special_chars():
    ords = list(range(33, 48)) + list(range(58, 65)) + \
           list(range(91, 97)) + list(range(123, 127)) + [1567]
    chrs = [chr(num) for num in ords]
    return set(chrs)

def get_all_puncts():
    return set(['?', '؟', '!', ':', ';', '-', '.', ','])

def get_all_non_puncts():
    return get_all_special_chars() - get_all_puncts()

def remove_extra_spaces(text):
    text = re.sub(" +", " ", text)
    return text

def add_spaces_to_all_special_chars(text):
    # even English
    text = re.compile('([^\n\u0621-\u064A0-9])').sub(r' \1 ', text)
    return text

def save_list(list, file_name):
    open(file_name, 'w').write(('\n').join(list))

def segment(text):
    # suppress farasa stdout
    # WARNING: this is LINUX ONLY command!
    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    segmenter = FarasaSegmenter(interactive=True)
    # resume farasa stdout
    sys.stdout = old_stdout

    return segmenter.segment(text)

def clean(segment = False, special_chars = False, 
            english = False, normalize = False):

    if segment:
        text = segment(text)
    if not english:
        text = remove_english_chars(text)
    if normalize:
        text = normalize_data(text)

    text = add_spaces_to_all_special_chars(text)
    text = remove_extra_spaces(text)
    return text 
    



