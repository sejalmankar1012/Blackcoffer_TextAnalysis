# -*- coding: utf-8 -*-
"""Text analysis BlackCoffer .ipynb
"""

import numpy as np 
import re 
import os 
import pandas as pd
from nltk.tokenize import RegexpTokenizer , sent_tokenize
from urllib.request import urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import urllib.request,sys,time ,requests

stopWordsFile =     '/content/StopWords_Generic.txt'
positiveWordsFile = '/content/positive-words.txt'
nagitiveWordsFile = '/content/negative-words.txt'

input = pd.read_excel("/content/Input.xlsx")
input

def get_article_names(urls):
  titles = []
  for i in range (len(urls)):
    title = urls[i]
    title_clean = title[title.index( "m/" ) + 2 :-1]. replace('-' , ' ')
    titles.append(title_clean)
  return titles

urls =input["URL"]
urlsTitleDF = get_article_names(urls)
urlsTitleDF

url = "https://insights.blackcoffer.com/how-people-diverted-to-telehealth-services-and-telemedicine"

page=requests.get(url , headers={"User-Agent": "XY"})  
soup = BeautifulSoup(page.text , 'html.parser')
#get title
title = soup . find("h1",attrs = { 'class' : 'entry-title'}).get_text()

#get article text
text = soup . find(attrs = { 'class' : 'td-post-content'}).get_text()
# break into lines and remove leading and trailing space on each
lines = (line.strip() for line in text.splitlines())
# break multi-headlines into a line each
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
# drop blank lines
text = '\n'.join(chunk for chunk in chunks if chunk)

# Loading positive words
with open(positiveWordsFile,'r') as posfile:
    positivewords=posfile.read().lower()
positiveWordList=positivewords.split('\n')


# Loading negative words
with open(nagitiveWordsFile ,'r' ,  encoding="ISO-8859-1") as negfile:
    negativeword=negfile.read().lower()
negativeWordList=negativeword.split('\n')

#Loading stop words dictionary for removing stop words

with open(stopWordsFile ,'r') as stop_words:
    stopWords = stop_words.read().lower()
stopWordList = stopWords.split('\n')
stopWordList[-1:] = []



display( positiveWordList[:6]  , negativeWordList[:6] , stopWordList[:6])

#tokenizeing module and filtering tokens using stop words list, removing punctuations
def tokenizer(text):
    text = text.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)
    filtered_words = list(filter(lambda token: token not in stopWordList, tokens))
    return filtered_words

def positive_score (text):
  posword=0
  tokenphrase = tokenizer(text)
  for word in tokenphrase :
    if word in positiveWordList:
       posword+=1
      
    retpos = posword
    return retpos 

def negative_score (text):
  negword=0
  tokenphrase = tokenizer(text)
  for word in tokenphrase :
    if word in negativeWordList : negword +=1

    retneg = negword 
    return retneg

def polarity_score (positive_score , negative_score) :
  return (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
#################################################
def total_word_count(text):
    tokens = tokenizer(text)
    return len(tokens)
#############################################
def AverageSentenceLenght (text):
  Wordcount = len(tokenizer (text))
  SentenceCount = len (sent_tokenize(text))
  if SentenceCount > 0 : Average_Sentence_Lenght = Wordcount / SentenceCount

  avg = Average_Sentence_Lenght

  return round(avg)


# Counting complex words
def complex_word_count(text):
    tokens = tokenizer(text)
    complexWord = 0
    
    for word in tokens:
        vowels=0
        if word.endswith(('es','ed')):
            pass
        else:
            for w in word:
                if(w=='a' or w=='e' or w=='i' or w=='o' or w=='u'):
                    vowels += 1
            if(vowels > 2):
                complexWord += 1
    return complexWord

def percentage_complex_word(text):
    tokens = tokenizer(text)
    complexWord = 0
    complex_word_percentage = 0
    
    for word in tokens:
        vowels=0
        if word.endswith(('es','ed')):
            pass
        else:
            for w in word:
                if(w=='a' or w=='e' or w=='i' or w=='o' or w=='u'):
                    vowels += 1
            if(vowels > 2):
                complexWord += 1
    if len(tokens) != 0:
        complex_word_percentage = complexWord/len(tokens)
    
    return complex_word_percentage

def fog_index(averageSentenceLength, percentageComplexWord):
    fogIndex = 0.4 * (averageSentenceLength + percentageComplexWord)
    return fogIndex

URLS = input ["URL"]
URLS

corps =[]
for url in URLS:

  page=requests.get(url , headers={"User-Agent": "XY"})  
  soup = BeautifulSoup(page.text , 'html.parser')
  #get title
  title = soup . find("h1",attrs = { 'class' : 'entry-title'}).get_text()

  #get article text
  text = soup . find(attrs = { 'class' : 'td-post-content'}).get_text()
  # break into lines and remove leading and trailing space on each
  lines = (line.strip() for line in text.splitlines())
  # break multi-headlines into a line each
  chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
  # drop blank lines
  text = '\n'.join(chunk for chunk in chunks if chunk)
  corps.append(text)

#df = pd.DataFrame(corps,urlsTitleDF)
df = pd.DataFrame({'title':urlsTitleDF,'corps': corps})
df["total word count"] = df["corps"] . apply (total_word_count)
df["percentage_complex_word"] = df["corps"] . apply (percentage_complex_word)
df["complex_word_count"] = df["corps"] . apply (complex_word_count)
df["AverageSentenceLenght"] = df["corps"] . apply (AverageSentenceLenght)
df["positive_score"] = df["corps"] . apply (positive_score)
df["negative_score"] = df["corps"] . apply (negative_score)
df["polarity_score"] = np.vectorize(polarity_score)(df['positive_score'],df['negative_score'])

df

final = df.drop("corps" , 1)
final

final.to_excel('Output Data Structure.xlsx', encoding='utf-8')

