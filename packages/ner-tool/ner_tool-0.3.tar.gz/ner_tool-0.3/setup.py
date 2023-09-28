from setuptools import setup

setup(
    name='ner_tool',
    version='0.3',
    packages=['ner_tool'],
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
    'scipy',
    'six'
]
)
