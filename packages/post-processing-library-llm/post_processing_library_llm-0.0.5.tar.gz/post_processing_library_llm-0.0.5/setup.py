from setuptools import setup

setup(
    name='post_processing_library_llm',
    version='0.0.5',
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
    description="A brief description of package",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst"

)
