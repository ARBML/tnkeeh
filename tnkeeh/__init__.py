import tnkeeh.tnkeeh as tn

from tnkeeh.tnkeeh import (
    clean_data,
    _clean_text,
    clean_data_frame,
    read_data,
    split_raw_data,
    clean_hf_dataset,
    split_parallel_data,
    split_classification_data,
)

class Tnqeeh:
    def __init__(
        self, segment = False, remove_special_chars = False, 
        remove_english = False, normalize = False, remove_diacritics = False,
        execluded_chars = [], remove_tatweel = False, remove_html_elements = False,
        remove_links = False, remove_twitter_meta = False, remove_long_words = False,
        remove_repeated_chars = False
    ):
        self.args = locals()
        self.args.pop('self')

    def clean_hf_dataset(self, dataset, field):
        return tn.clean_hf_dataset(dataset, field, **self.args)
    
    def clean_text_file(self, file_path, save_path):
        return tn.clean_data(file_path,save_path, **self.args)

    def clean_raw_text(self, text):
        return tn._clean_text(text, **self.args),
        
    def clean_data_frame(self, df, column_name):
        return tn.clean_data_frame(df, column_name, **self.args)
    
