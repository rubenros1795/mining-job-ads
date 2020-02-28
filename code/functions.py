
###     PREPARATION     ####
from string import ascii_lowercase
import pandas as pd
from nltk import ngrams
import re
import pickle
import itertools

def ExtractWindows(df, list_words, qual_words,keyword_processor):
    alphabet_id = [c for c in ascii_lowercase]
    alphabet_id = [''.join(i) for i in itertools.product(alphabet_id, repeat = 5)]

    opd = dict()
    ctr = 0 # counter for showing progress

    for c,i in enumerate(df.clean):
        ctr += 1
        extracted_occupations = keyword_processor.extract_keywords(" ".join(i))
        extracted_occupations = [o for o in extracted_occupations if o in i]

        if len(extracted_occupations) > 0:     # check if there is an occupation in the advertisement

            for count,o in enumerate(extracted_occupations):                       # loop over occupations in ad-occupation list and select windows around 'em
                ind = i.index(o)
                sl = i[ind-12:ind+40]
                sl = ' '.join(sl)
                if 'loon ' in sl or 'salaris' in sl:               # if the word 'loon' is in the window; append [occupation:window] to list (not dictionary because of duplicate occupations)
                    output_list = [o, sl, df['id'][c], df['date'][c], df['image_url'][c], i, ind]
                    opd.update({str(c) + alphabet_id[count]:output_list})

        if ctr % 10000 == 0:                    # print the progress
            print(str(round(ctr / len(df.clean) * 100)) + "%")
    ## Convert output dictionary to dataframe (for clarity)
    dfa = pd.DataFrame([opd.keys() ,[v[3] for k,v in opd.items()], [v[0] for k,v in opd.items()], [v[1] for k,v in opd.items()],[v[4] for k,v in opd.items()], [' '.join(v[5]) for k,v in opd.items()],[v[6] for k,v in opd.items()],]).T
    dfa.columns = ['id','date', 'oc', 'window','image_url', 'ocr', 'occ_index']
    return dfa

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


##      CLASSIFICATION  ##
## Check Qualitative Indcators
def ExtractQual(string, qual_words):
    s= string.split(' ')
    loon = 'na'

    list_qualitative_wage_indicators=qual_words

    s_unigrams = s
    s_bigrams = ["_".join(list(i)) for i in ngrams(s, 2)]

    uni_bi= s_unigrams + s_bigrams

    if any(x in uni_bi for x in list_qualitative_wage_indicators):

        qualitative_wage = list([i for i in uni_bi if i in list_qualitative_wage_indicators])

        if len(qualitative_wage) > 0:
            loon = [loon for loon in list(set(qualitative_wage))]
            return loon

    else:
        loon = 'na'
        return loon

## Extract Numbers
def GetNum(string, wage_words):
    s = string.split(' ')
    all_numbers = []

    for i,w in enumerate(s):
        if hasNumbers(w) == True or w in wage_words:
            all_numbers.append([i, w])

    nonnum = NonNumbClass(string)

    if nonnum != "na":
        all_numbers.append(nonnum)
    else:
        pass
    return all_numbers

## Classify Numbers
def NumberCandidateClass(string, index, number_candidate):
    string = string.split(' ')
    ## Set Variables
    score = 0
    weights = 0
    features = []
    len_string = len(string) - 1
    number_candidate = str(number_candidate)
    # Negative
    if len(number_candidate) > 5:
        score += -1
        weights += 1
    if number_candidate[0:2] == "18" and len(number_candidate) == 4:
        score += -1
        weights += 1
    try:
        if string[index+1] in ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december']:
            score += -1
            weights += 1
    except IndexError:
        pass

    # Positive
    if string[index-1] == "f" or string[index-1] == 'ƒ':
        score += 1
        weights += 1
    if number_candidate[0] == "f" or number_candidate[0] == 'ƒ':
        score += 1
        weights += 1
    if string[index-1] == "van":
        score += 1
        weights += 1

    try:
        if string[index+1] == "gulden" or string[index+2] == "gulden":
            score += 1
            weights += 1
    except IndexError:
        pass

    if string[index-1] in ['loon', 'salaris','beloning','jaarwedde', 'provisie'] or string[index-2] in ['loon', 'salaris','beloning','jaarwedde', 'provisie']:
        score += 1
        weights += 1

    if string[index-1] == 'tegen' or string[index-2] == 'tegen':
        score += 1
        weights += 1

    try:
        if string[index+1] == "per" or string[index+2] == "per":
            weights += 1
            score += 1
    except IndexError:
        pass

    try:
        if string[index+1] == "ongeveer":
            score += 1
            weights += 1
    except IndexError:
        pass

    try:
        if string[index+1] in ['loon', 'salaris','beloning','jaarwedde'] or string[index+2] in ['loon', 'salaris','beloning','jaarwedde']:
            score += 2
            weights += 1
    except IndexError:
        pass

    #print(features)
    return score

def ExtractNum(string, wage_words):
    list_numbers = GetNum(string, wage_words)
    list_scores = list(zip([number for ind,number in list_numbers], [NumberCandidateClass(string, ind, number) for ind, number in list_numbers]))
    if len(list_scores) > 0 and max([score for loon,score in list_scores]) > 0:
        winning_number = max([score for loon,score in list_scores])
        loon =  [loon for loon,score in list_scores if score == winning_number][0]
    else:
        loon = "na"
    return loon

## Detect Non-Numerical
def NonNumbClass(string):
    s = string.split(' ')
    candidates = []

    f_instances = [w for w in s if "ƒ" in w and hasNumbers(w) == False]

    for f in f_instances:

        if len(f) > 1 and f[0] == 'ƒ':
            candidates.append(f)

        if len(f) == 1:
            f_index = s.index(f)

            try:
                if "o" in s[f_index + 1]:
                        candidates.append(" ".join(s[f_index:f_index + 1]))
            except IndexError:
                pass
    if len(candidates) == 0:
        candidates = "na"
        return candidates
    else:
        index_candidate = s.index(candidates[0])
        return [index_candidate,candidates[0]]

##      NORMALIZING      ##
## Confert Numerical and Non-Numerical Wages in Integers

def NormalizeNumbers(df):
    dfa = df
    for i in range(len(dfa)):
        if dfa['ex_num'][i] != "na":
            s = dfa['ex_num'][i]
            s = s.replace("o", "0")
            s = s.replace("l", "1")
            s = s.replace("—", "")
            s = ''.join([i for i in s if not i.isalpha()])
            s = re.sub(r'\W+', '', s)

            if len(s) > 0:
                dfa['ex_num'][i] = int(s)
            else:
                continue
        else:
            continue

    for i in range(len(dfa)):
        if dfa['ex_nonnum'][i] != "na":
            s = dfa['ex_nonnum'][i]
            s = s.replace("o", "0")
            s = s.replace("l", "1")
            s = s.replace("b", "10")
            s = s.replace("ƒ", "")
            s = ''.join([i for i in s if not i.isalpha()])
            s = re.sub(r'\W+', '', s)

            if len(s) > 0:
                dfa['ex_nonnum'][i] = int(s)
            else:
                continue
        else:
            continue

    return dfa
