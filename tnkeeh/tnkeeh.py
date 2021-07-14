import re
import os
import sys
import math
import pickle
import pandas 
import warnings
from pathlib import Path
from farasa.segmenter import FarasaSegmenter
from transformers import MarianMTModel, MarianTokenizer

# remove diacritics
def _remove_diacritics(text):
    text = re.sub(r"[ًًٌٍَُِّْ]", "", text)
    return text

# normalize data
def _normalize_data(text):
    rel_path = os.path.dirname(__file__)
    norm_dict_path = os.path.join(rel_path, "dictionaries/norm_dict.pl")
    norm_dict = pickle.load(open(norm_dict_path, "rb"))
    # use a mapping dictionary
    regex = re.compile("|".join(map(re.escape, norm_dict.keys())))
    text = regex.sub(lambda match: norm_dict[match.group(0)], text)
    return text


# remove English characters
def _remove_english_chars(text):
    return re.sub("[a-zA-Z]", "", text)


def _remove_digits(text):
    return re.sub("[0-9]", "", text)


def _remove_all_english(text):
    return re.sub("[a-zA-Z0-9]", "", text)


def _keep_only_arabic_chars(text):
    text = re.compile("([\n\u0621-\u064A0-9])").sub(r" ", text)
    return text


# https://github.com/google-research/bert/blob/master/tokenization.py
def _get_all_special_chars():
    ords = (
        list(range(33, 48))
        + list(range(58, 65))
        + list(range(91, 97))
        + list(range(123, 127))
        + [1567, 1548]
    )
    chrs = [chr(num) for num in ords]
    return chrs


def _get_all_puncts():
    return ["?", "؟", "!", ":", ";", "-", ".", ",", "،"]


def _get_all_non_puncts():
    return list(set(_get_all_special_chars()) - set(_get_all_puncts()))


def _remove_extra_spaces(text):
    text = re.sub(" +", " ", text)
    return text


def _remove_special_chars(text, excluded_chars=[]):
    regex_special_chars = "\\^+*[]-"
    ignored_chars = ""
    for char in excluded_chars:
        if char in regex_special_chars:
            ignored_chars += f"\\" + char
        else:
            ignored_chars += char
    return re.compile("([^\n\u0621-\u064A0-9a-zA-Z " + ignored_chars + "])").sub(
        " ", text
    )


def _add_spaces_to_all_special_chars(text):
    text = re.compile("([^\n\u0621-\u064A0-9a-zA-Z ])").sub(r" \1 ", text)
    return text


def save_list(list, file_name):
    open(file_name, "w").write(("\n").join(list))


def _remove_html_elements(text):
    cleanr = re.compile("<.*?>")
    text = re.sub(cleanr, "", text)
    return text


def _farasa_segment(text, segmenter):
    return segmenter.segment(text)


def _remove_empty_lines(text):
    lines = text.split("\n")
    return ("\n").join([line for line in lines if len(line) > 1])


# https://stackoverflow.com/a/11332580
def _remove_links(text):
    text = re.sub(r"http\S+", " ", text, flags=re.MULTILINE)
    return text


def _remove_twitter_meta(text):
    text = re.sub("(@[A-Za-z0-9]+)", " ", text)
    text = re.sub("(#[A-Za-z0-9]+)", " ", text)
    text = _remove_links(text)
    return text


def _remove_long_words(text, threshold=15):
    return (" ").join(word for word in text.split(" ") if len(word) < threshold)

def _translate(text):
    global model, tokenizer
    translated = model.generate(**tokenizer(text, return_tensors="pt", padding='max_length', truncation=True))
    return tokenizer.decode(translated[0], skip_special_tokens=True)

def _clean_text(text, **kwargs):
    if kwargs['segment']:
        # suppress farasa stdout
        # WARNING: this is LINUX ONLY command!
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        segmenter = FarasaSegmenter(interactive=True)
        # resume farasa stdout
        sys.stdout = old_stdout

    if kwargs['remove_repeated_chars']:
        text = _remove_repeated_chars(text)
    if kwargs['remove_html_elements']:
        text = _remove_html_elements(text)
    if kwargs['segment']:
        text = _farasa_segment(text, segmenter)
    if kwargs['remove_english']:
        text = _remove_english_chars(text)
    if kwargs['normalize']:
        text = _normalize_data(text)
    if kwargs['remove_diacritics']:
        text = _remove_diacritics(text)
    if kwargs['remove_special_chars']:
        text = _remove_special_chars(text, kwargs['excluded_chars'])
    if kwargs['remove_tatweel']:
        text = re.sub('ـ', '', text)
    if kwargs['remove_links']:
        text = _remove_links(text)
    if kwargs['remove_twitter_meta']:
        text = _remove_twitter_meta(text)
    if kwargs['remove_long_words']:
        text = _remove_long_words(text)
    if kwargs['translate'] != None:
        text = _translate(text)

    text = _add_spaces_to_all_special_chars(text)
    text = _remove_extra_spaces(text)
    return text 

def _clean_list(list, **kwargs):
    cleaned_list = []

    for text in list:
        text = _clean_text(text, **kwargs)
        cleaned_list.append(text)
    return cleaned_list

def _clean_dict(example, field, **kwargs):
    example[field] = _clean_text(example[field], **kwargs)
    return example

def clean_hf_dataset(dataset, field, segment = False, remove_special_chars = False, 
        remove_english = False, normalize = False, remove_diacritics = False,
        excluded_chars = [], remove_tatweel = False, remove_html_elements = False,
        remove_links = False, remove_twitter_meta = False, remove_long_words = False,
        remove_repeated_chars = False, translate = None):
    args = locals()
    args.pop('dataset')
    args.pop('field')
    if translate!= None:
        global model, tokenizer
        model_name = f'Helsinki-NLP/opus-mt-ar-{translate}'
        tokenizer = MarianTokenizer.from_pretrained(model_name, model_max_length = 512)
        model = MarianMTModel.from_pretrained(model_name)

    updated_dataset = dataset.map(lambda example:_clean_dict(example, field, **args))
    return updated_dataset

def clean_data_frame(df, column_name, segment = False, remove_special_chars = False, 
        remove_english = False, normalize = False, remove_diacritics = False,
        excluded_chars = [], remove_tatweel = False, remove_html_elements = False,
        remove_links = False, remove_twitter_meta = False, remove_long_words = False,
        remove_repeated_chars = False, translate = None):
    df[column_name] = list(_clean_list(df[column_name], **locals()))
    return df 

# https://stackoverflow.com/a/10072826
def _remove_repeated_chars(text):
    return re.sub(r"(.)\1+", r"\1\1", text)

def _normalize_dots(text):
    dots_letters = {
        "ب": list("بتثين"),
        "ح": list("جحخ"),
        "د": list("دذ"),
        "ر": list("رز"),
        "س": list("سش"),
        "ص": list("صض"),
        "ط": list("طظ"),
        "ع": list("عغ"),
        "ف": list("فق"),
        # "ا": list("اأإآئءوى"),
        "ا": list('اأإئآؤء'),
        'ه': list('ةه'),
    }
    # convert dots_letters dict to letter-to-letter map
    letters_map = dict(
        {
            letter: k
            for k, letters_list in dots_letters.items()
            for letter in letters_list
        }
    )
    normalized_text = text.translate(str.maketrans(letters_map))
    return normalized_text


def clean_data(
    file_path,
    save_path,
    segment=False,
    remove_special_chars=False,
    remove_english=False,
    normalize=False,
    remove_diacritics=False,
    excluded_chars=[],
    remove_tatweel=False,
    remove_html_elements=False,
    remove_links=False,
    remove_twitter_meta=False,
    remove_long_words=False,
    remove_repeated_chars=False,
    by_chunk=False,
    chunk_size=100000,
    normalize_dots=False,
):

    assert file_path
    assert save_path

    if segment:
        # suppress farasa stdout
        # WARNING: this is LINUX ONLY command!
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        segmenter = FarasaSegmenter(interactive=True)
        # resume farasa stdout
        sys.stdout = old_stdout

    with open(file_path, "r") as f:
        i = 0
        while True:
            if by_chunk:
                text = ("").join(f.readlines(chunk_size))
            else:
                text = f.read()

            if len(text) == 0:
                break

            if remove_repeated_chars:
                print("Remove repeated chars")
                text = _remove_repeated_chars(text)
            if remove_html_elements:
                print("Remove HTML elements")
                text = _remove_html_elements(text)
            if segment:
                print("Segment data")
                text = _farasa_segment(text, segmenter)
            if remove_english:
                print("Remove English chars")
                text = _remove_english_chars(text)
            if normalize:
                print("Normalize data")
                text = _normalize_data(text)
            if remove_diacritics:
                print("Remove diacritics")
                text = _remove_diacritics(text)
            if remove_special_chars:
                print("Remove special chars")
                text = _remove_special_chars(text, excluded_chars)
            if remove_tatweel:
                print("Remove tatweel")
                text = re.sub("ـ", "", text)
            if remove_links:
                print("Remove links")
                text = _remove_links(text)
            if remove_twitter_meta:
                print("Remove twitter meta")
                text = _remove_twitter_meta(text)
            if remove_long_words:
                print("Remove long words")
                text = _remove_long_words(text)
            if normalize_dots:
                print('normalizing dots')
                text = _normalize_dots(text)

            text = _add_spaces_to_all_special_chars(text)
            text = _remove_extra_spaces(text)
            text = _remove_empty_lines(text)

            if by_chunk:
                path = save_path.replace(".txt", f"_{i}.txt")
                print(f"Saving chunk to {path}")
                open(path, "w").write(text)
            else:
                print(f"Saving to {save_path}")
                open(save_path, "w").write(text)
            i += 1


def split_raw_data(data_path, split_ratio=0.8):
    data = open(data_path, "r").read()

    train_data = data[: int(split_ratio * len(data))]
    test_data = data[int(split_ratio * len(data)):]

    print("Save to data")
    Path("data").mkdir(parents=True, exist_ok=True)
    open("data/train.txt", "w").write(train_data)
    open("data/test.txt", "w").write(test_data)


def split_classification_data(data_path, lbls_path, split_ratio=0.8):

    data = open(data_path, "r").read().splitlines()
    lbls = open(lbls_path, "r").read().splitlines()

    assert len(data) == len(lbls)

    print("Split data")
    train_data = ("\n").join(data[: int(split_ratio * len(data))])
    train_lbls = ("\n").join(lbls[: int(split_ratio * len(lbls))])

    test_data = ("\n").join(data[int(split_ratio * len(data)):])
    test_lbls = ("\n").join(lbls[int(split_ratio * len(data)):])

    print("Save to data")
    Path("data").mkdir(parents=True, exist_ok=True)
    open("data/train_data.txt", "w").write(train_data)
    open("data/train_lbls.txt", "w").write(train_lbls)

    open("data/test_data.txt", "w").write(test_data)
    open("data/test_lbls.txt", "w").write(test_lbls)


def split_parallel_data(input_path, target_path, split_ratio=0.8):

    inp_data = open(input_path, "r").read().splitlines()
    tar_data = open(target_path, "r").read().splitlines()

    assert len(inp_data) == len(tar_data)

    print("Split data")
    train_inp_data = ("\n").join(inp_data[: int(split_ratio * len(inp_data))])
    train_tar_data = ("\n").join(tar_data[: int(split_ratio * len(inp_data))])

    test_inp_data = ("\n").join(inp_data[int(split_ratio * len(inp_data)):])
    test_tar_data = ("\n").join(tar_data[int(split_ratio * len(inp_data)):])

    print("Save to data")
    Path("data").mkdir(parents=True, exist_ok=True)
    open("data/train_inp_data.txt", "w").write(train_inp_data)
    open("data/train_tar_data.txt", "w").write(train_tar_data)

    open("data/test_inp_data.txt", "w").write(test_inp_data)
    open("data/test_tar_data.txt", "w").write(test_tar_data)


def read_data(data_path="data", mode=0):
    files = os.listdir(data_path)

    if mode == 0:
        train_data = open(f"data/train.txt").read()
        test_data = open(f"data/test.txt").read()
        return train_data, test_data
    elif mode == 1:
        print("Read data ", files)
        train_data = open(f"data/train_data.txt").read().splitlines()
        train_lbls = open(f"data/train_lbls.txt").read().splitlines()

        test_data = open(f"data/test_data.txt").read().splitlines()
        test_lbls = open(f"data/test_lbls.txt").read().splitlines()

        return train_data, test_data, train_lbls, test_lbls
    elif mode == 2:
        print("Read data ", files)
        train_inp_data = open(f"data/train_inp_data.txt").read().splitlines()
        train_tar_data = open(f"data/train_tar_data.txt").read().splitlines()

        test_inp_data = open(f"data/test_inp_data.txt").read().splitlines()
        test_tar_data = open(f"data/test_tar_data.txt").read().splitlines()

        return train_inp_data, train_tar_data, test_inp_data, test_tar_data
