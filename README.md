 <p align="center"> 
 <img src = "logo.png" width = "200px"/>
 </p>

**tnkeeh** (تنقيح) is an Arabic preprocessing library for python. It was designed using `re` for creating quick replacement expressions for several examples.

## Features
* Quick cleaning
* Segmentation
* Normalization 
* Data splitting 

## Examples

### Data Cleaning 

```python
import tnkeeh as tn
tn.clean_data(file_path = 'data.txt', save_path = 'cleaned_data.txt',)
```
Arguments

* `segment` uses farasa for segmentation. 
* `remove_diacritics` removes all diacritics. 
* `remove_special_chars` removes all sepcial chars. 
* `remove_english` removes english alphabets and digits. 
* `normalize` match digits that have the same writing but different encodings. 
* `remove tatweel` tatweel character `ـ` is used a lot in arabic writing.  

### Data Splitting 
Splits raw data into training and testing using the `split_ratio`
```python
import tnkeeh as tn
tn.split_raw_data(data_path, split_ratio = 0.8)
```

Splits data and labels into training and testing using the `split_ratio`

```python
import tnkeeh as tn
tn.split_classification_data(data_path, lbls_path, split_ratio = 0.8)
```

Splits input and target data with ration `split_ratio`. Commonly used for translation 

```python
tn.split_parallel_data('ar_data.txt','en_data.txt')

```

### Data Reading
Read split data, depending if it was raw or classification

```python
import tnkeeh as tn
train_data, test_data = tn.read_data(mode = 0)
```

Arguments

* `mode = 0` read raw data. 
* `mode = 1` read labeled data. 
* `mode = 2` read parallel data. 

## Contribution 
This is an open source project where we encourage contributions from the community. 

## License
[MIT](LICENSE) license. 

## Citation
```
@misc{tnkeeh2020,
  author = {Zaid Alyafeai and Maged Saeed},
  title = {tkseem: A Preprocessing Library for Arabic.},
  year = {2020},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/ARBML/tnkeeh}}
}
```



