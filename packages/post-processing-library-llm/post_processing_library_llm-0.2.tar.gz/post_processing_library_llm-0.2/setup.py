from setuptools import setup

setup(
    name='post_processing_library_llm',
    version='0.2',
    packages=['post_processing_library_llm'],
    install_requires=[
    'fuzzywuzzy',
    'Levenshtein',
    'nltk',
    'numpy',
    'pandas',
    'python-dateutil',
    'pytz==2023.3.post1',
    'rapidfuzz',
    'regex',
    'scikit-learn',
    'scipy'
],
description='''\
# post-processing-library-llm

post-processing-library-llm is a Python package for performing Named Entity Recognition and text matching tasks. It provides useful functionality for...

## Features
- Named Entity Recognition with fuzzy matching
- Text matching with various algorithms

- import this method to do NER "from post_processing_library_llm.ner import ner"
- import this method to get metrics  "from post_processing_library_llm.get_metrics import text_matcher"

## How you can use?
- To get NER Results "ner.named_entity_recognition(truth_dict, prediction_dict, fuzzy_threshold)"
- To get the metrics  "text_matcher.match_texts(truth_list, pred_list, 'direct_match')"
'''

)
