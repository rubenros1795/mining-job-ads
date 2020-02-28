import os, glob, pandas as pd
import string, re
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from string import ascii_lowercase
import requests
import shutil
import pandas as pd
import time
from nltk import ngrams
from operator import itemgetter
from functions import *
import pickle
from flashtext import KeywordProcessor

'''
Code for 'Mining Wages in Nineteenth-Century Job Advertisements: The Application of Language Resources and Language Technologyto study Economic and Social Inequality'.
Paper Submitted to "LR4SSHOC: LREC2020 workshop about Language Resources for the SSH Cloud”

Code made by Ruben Ros, 2019-2020

This script uses resources (vocabularies of wage indicators and occupation titles stored in the '/resources' folder. The classifier takes .csv files as input, stored in the same folder as this script.)
'''

base_path = os.getcwd()

# Tokenization
def clean_and_split_str(txt):
    translator = str.maketrans('', '', string.punctuation)
    txt = txt.translate(translator)
    txt = re.sub('\s+', ' ', txt).strip()
    txt = txt.lower()
    txt = txt.split(' ')
    return str(txt)

# Import Resources
with open('path/to/resources/stopwords-nl.txt', encoding = 'utf-8') as f:
    stopz = f.read().splitlines()

with open('path/to/resources/list_occupations.txt', 'r') as f:
    list_oc = f.readlines()
    list_oc = list(set([o.replace('\n','') for o in list_oc]))
    list_oc =  [clean_and_split_str(l) for l in list_oc]
    list_oc = list(set([l for l in list_oc if len(l.split(' ')) == 1 and l not in stopz] + ['keukenmeid', 'loopjongen','bode','dienstmeid','meid']))
    print("occupations", len(list_oc))

keyword_processor = KeywordProcessor()
for w in list_oc:
    keyword_processor.add_keyword(w)

# Import QUAL Indicator list
with open('path/to/resources/wage_indicators.txt', encoding = 'utf-8') as f:
    wage_words = f.read().splitlines()


## Loop over decades
# Every decades has multiple .csvs, hence the nested loop.

for year in ['1850s','1860s','1870s']:
    data_path = os.path.join(base_path,year)
    list_data = [f for f in os.listdir(data_path) if ".csv" in f and "_processed" not in f] # check for csvs already processed

    for csv in list_data:
        df = pd.read_csv(os.path.join(data_path, csv), sep='\t')

        # clean the advertisements
        df['clean'] = [clean_and_split_str(i) for i in list(df['ocr'])]

        # extract windows
        dfa = ExtractWindows(df, list_words,qual_words, keyword_processor)
        print("windows extracted")

        # classify
        dfa['ex_qual'] = ""
        dfa['ex_num'] = ""

        for i in range(len(dfa)):

            dfa['ex_qual'][i] = ExtractQual(dfa['window'][i], qual_words)
            dfa['ex_num'][i] = ExtractNum(dfa['window'][i], wage_words)

        # Postprocess the extracted indicators
        dfa = NormalizeNumbers(dfa)

        fn = csv[:-4] + "_processed.csv"
        dfa.to_csv(fn, index = False)
