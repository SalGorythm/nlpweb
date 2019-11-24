#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
import sqlite3
conn = sqlite3.connect('nlp_learn.db')

# data = pd.read_csv('abcnews-date-text.csv', error_bad_lines=False);
query = "SELECT id, title FROM books"
result_set = conn.execute(query).fetchall()
data = pd.DataFrame(result_set, columns = ['id', 'title'])

data_text = data[['title']]
data_text['index'] = data_text.index
documents = data_text


# In[5]:


len(documents)


# In[6]:


documents[:5]


# In[7]:


import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import numpy as np
np.random.seed(2018)


# In[8]:


import nltk
nltk.download('wordnet')


# In[9]:


print(WordNetLemmatizer().lemmatize('went', pos='v'))


# In[10]:


stemmer = SnowballStemmer('english')
original_words = ['caresses', 'flies', 'dies', 'mules', 'denied','died', 'agreed', 'owned', 
           'humbled', 'sized','meeting', 'stating', 'siezing', 'itemization','sensational', 
           'traditional', 'reference', 'colonizer','plotted']
singles = [stemmer.stem(plural) for plural in original_words]
pd.DataFrame(data = {'original word': original_words, 'stemmed': singles})


# In[11]:


def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 1:
            result.append(lemmatize_stemming(token))
    return result


# In[26]:


doc_sample = documents[documents['index'] == 4130].values[0][0]

print('original document: ')
words = []
for word in doc_sample.split(' '):
    words.append(word)
print(words)
print('\n\n tokenized and lemmatized document: ')
print(preprocess(doc_sample))


# In[27]:


processed_docs = documents['title'].map(preprocess)


# In[28]:


processed_docs[:10]


# In[29]:


dictionary = gensim.corpora.Dictionary(processed_docs)
len(dictionary)


# In[30]:


count = 0
for k, v in dictionary.iteritems():
    print(k, v)
    count += 1
    if count > 10:
        break


# In[31]:


dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)


# In[32]:


bow_corpus = [dictionary.doc2bow(doc) for doc in processed_docs]
bow_corpus[4130]


# In[36]:


bow_doc_4310 = bow_corpus[4130]

for i in range(len(bow_doc_4310)):
    print("Word {} (\"{}\") appears {} time.".format(bow_doc_4310[i][0], 
                                                     dictionary[bow_doc_4310[i][0]], 
                                                     bow_doc_4310[i][1]))


# In[37]:


from gensim import corpora, models

tfidf = models.TfidfModel(bow_corpus)


# In[38]:


corpus_tfidf = tfidf[bow_corpus]


# In[39]:


from pprint import pprint

for doc in corpus_tfidf:
    pprint(doc)
    break


# In[42]:


print("Running LDA using Bag of Words")
lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=25, id2word=dictionary, passes=2, workers=2)
print("LDA Training - Complete")


# In[43]:


for idx, topic in lda_model.print_topics(-1):
    print('Topic: {} \nWords: {}'.format(idx, topic))


# In[45]:


print("Running LDA using TF-IDF")
lda_model_tfidf = gensim.models.LdaMulticore(corpus_tfidf, num_topics=25, id2word=dictionary, passes=2, workers=4)
print("LDA Training - Complete")


# In[46]:


for idx, topic in lda_model_tfidf.print_topics(-1):
    print('Topic: {} Word: {}'.format(idx, topic))


# In[48]:


print("Performance evaluation by classifying sample document using LDA TF-IDF model")
for index, score in sorted(lda_model_tfidf[bow_corpus[4130]], key=lambda tup: -1*tup[1]):
    print("\nScore: {}\t \nTopic: {}".format(score, lda_model_tfidf.print_topic(index, 10)))


# In[62]:


print("Testing model on unseen document")
unseen_document = 'The Free Voice'
bow_vector = dictionary.doc2bow(preprocess(unseen_document))
print(lda_model[bow_vector])
print("________________________________________________________________________________________________")
for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1]):
    print("Score: {}\t Topic: {}".format(score, lda_model.print_topic(index, 5)))


# In[27]:


a = "Salman's bag"
a.replace("'", "")


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




