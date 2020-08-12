import re
import os
import sys
import math
import pickle
import warnings
from pathlib import Path
from farasa.segmenter import FarasaSegmenter

# remove diacritics
def _remove_diacritics(text):
    text = re.sub(r"[ًٌٍَََُِّْ]", "", text)
    return text

# normalize data
def _normalize_data(text):
    rel_path = os.path.dirname(__file__)
    norm_dict_path = os.path.join(
        rel_path, "dictionaries/norm_dict.pl"
    )
    norm_dict = pickle.load(open(norm_dict_path, "rb"))
    # use a mapping dictionary 
    regex = re.compile("|".join(map(re.escape, norm_dict.keys())))
    text  = regex.sub(lambda match: norm_dict[match.group(0)], text)
    return text 

# remove English characters 
def _remove_english_chars(text):
    return re.sub('[a-zA-Z]', '', text)

def _remove_digits(text):
    return re.sub('[0-9]', '', text)

def _remove_all_english(text):
   return re.sub('[a-zA-Z0-9]', '', text) 

def _keep_only_arabic_chars(text):
    text = re.compile('([\n\u0621-\u064A0-9])').sub(r' ', text)
    return text

# https://github.com/google-research/bert/blob/master/tokenization.py
def _get_all_special_chars():
    ords = list(range(33, 48)) + list(range(58, 65)) + \
           list(range(91, 97)) + list(range(123, 127)) + [1567, 1548]
    chrs = [chr(num) for num in ords]
    return chrs

def _get_all_puncts():
    return ['?', '؟', '!', ':', ';', '-', '.', ',', '،']

def _get_all_non_puncts():
    return list(set(_get_all_special_chars()) - set(_get_all_puncts()))

def _remove_extra_spaces(text):
    text = re.sub(" +", " ", text)
    return text

def _remove_special_chars(text, execluded_chars = []):
    return re.compile('([^\n\u0621-\u064A0-9 '+('').join(execluded_chars)+
                        '])').sub('', text)

def _add_spaces_to_all_special_chars(text):
    text = re.compile('(['+('').join(_get_all_special_chars())+'])').sub(r' \1 ', text)
    return text

def save_list(list, file_name):
    open(file_name, 'w').write(('\n').join(list))

def _farasa_segment(text):
    # suppress farasa stdout
    # WARNING: this is LINUX ONLY command!
    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    segmenter = FarasaSegmenter(interactive=True)
    # resume farasa stdout
    sys.stdout = old_stdout

    return segmenter.segment(text)

def clean_data(file_path, save_path, segment = False, remove_special_chars = False, 
        remove_english = False, normalize = False, remove_diacritics = False,
        execluded_chars = [], remove_tatweel = True):

    assert file_path
    assert save_path

    text = open(file_path , 'r').read()

    if segment:
        print('Segmenting data')
        text = _farasa_segment(text)
    if remove_english:
        print('Remove English Chars')
        text = _remove_english_chars(text)
    if normalize:
        print('Normalize data')
        text = _normalize_data(text)
    if remove_special_chars:
        print('Remove special characters')
        text = _remove_special_chars(text, execluded_chars)
    if remove_diacritics:
        print('Remove diacritics')
        text = _remove_diacritics(text)
    if remove_tatweel:
        print('Remove Tatweel')
        text = re.sub('ـ', '', text)

    text = _add_spaces_to_all_special_chars(text)
    text = _remove_extra_spaces(text)
    print(f'Saving to {save_path}')
    open(save_path, 'w').write(text)

def split_raw_data(data_path, split_ratio = 0.8):
    data = open(data_path, 'r').read()

    train_data = data[:int(split_ratio*len(data))]
    test_data  = data[int(split_ratio*len(data)):]

    open('data/train.txt', 'w').write(train_data)
    open('data/test.txt', 'w').write(test_data)

def split_classification_data(data_path, lbls_path, split_ratio = 0.8):
    
    data = open(data_path, 'r').read().splitlines()
    lbls  = open(lbls_path, 'r').read().splitlines()
    
    assert len(data) == len(lbls)

    print('Split data')
    train_data = ('\n').join(data[:int(split_ratio*len(data))])
    train_lbls = ('\n').join(lbls[:int(split_ratio*len(lbls))])

    test_data = ('\n').join(data[int(split_ratio*len(data)):])
    test_lbls = ('\n').join(lbls[int(split_ratio*len(data)):])

    print('Save to data')
    Path("data").mkdir(parents=True, exist_ok=True)
    open('data/train_data.txt', 'w').write(train_data)
    open('data/train_lbls.txt', 'w').write(train_lbls)

    open('data/test_data.txt', 'w').write(test_data)
    open('data/test_lbls.txt', 'w').write(test_lbls)

def read_data(data_path = 'data'):
    files = os.listdir(data_path)

    if 'train.txt' in files:
        train_data = open(f'data/train.txt').read()
        test_data  = open(f'data/test.txt').read()
        return train_data, test_data
    else:
        print('Read data ', files)
        train_data = open(f'data/train_data.txt').read().splitlines()
        train_lbls = open(f'data/train_lbls.txt').read().splitlines()

        test_data = open(f'data/test_data.txt').read().splitlines()
        test_lbls = open(f'data/test_lbls.txt').read().splitlines()

        return train_data, test_data, train_lbls, test_lbls 
