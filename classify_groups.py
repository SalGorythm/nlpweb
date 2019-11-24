import pandas as pd

import gensim
from nltk.stem import WordNetLemmatizer, SnowballStemmer
import sqlite3

stemmer = SnowballStemmer('english')


def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))


def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 1:
            result.append(lemmatize_stemming(token))
    return result


print("Testing model on unseen document")
conn = sqlite3.connect('nlp_learn.db')
filename = "trained_model/lda_train_bow.model"
lda_model = gensim.models.LdaModel.load(filename)
query = "SELECT id, title FROM books where groups is NULL"
result_set = conn.execute(query).fetchall()

data = pd.DataFrame(result_set, columns=['id', 'title'])
data_text = data[['title']]
data_text['index'] = data_text.index
documents = data_text

processed_docs = documents['title'].map(preprocess)
dictionary = gensim.corpora.Dictionary(processed_docs)
dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)

for row in result_set:

    unseen_document = row[1]
    bow_vector = dictionary.doc2bow(preprocess(unseen_document))

    groups = []
    group_count = 0
    for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1]):
        groups.append(str(index))

    query = "UPDATE books SET groups='{}' WHERE id={}".format(", ".join(groups[:5]), row[0])
    print("Updated id = {}".format(row[0]))

    conn.execute(query)
    conn.commit()

conn.close()