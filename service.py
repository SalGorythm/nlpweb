import math

import pandas as pd
import sqlite3
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import numpy as np
from models import BooksModel
from pandas import DataFrame
import xml.etree.ElementTree as ET


class Books:
    def __init__(self):
        self.model = BooksModel()

    def create(self, params):
        return self.model.create(params)

    def delete(self, item_id):
        return self.model.delete(item_id)

    def list(self):
        response = self.model.list_items()
        return response

    def list_books_in_group(self, group):
        response = self.model.list_books_in_group(group)
        return response


class ExportData:
    """
    1 - All Data
    2 - Titles
    3 - Authors
    """
    def __init__(self):
        self.data = Books().list()

    def export_csv(self, export_type):
        data = {"title": [], "author": []}
        for obj in self.data:
            data["title"].append(obj["title"])
            data["author"].append(obj["author"])

        if int(export_type) == 2:
            df = DataFrame(data, columns=["title"])
        elif int(export_type) == 3:
            df = DataFrame(data, columns=["author"])
        else:
            df = DataFrame(data, columns=["title", "author"])
        df.to_csv(r'static\export_data.csv', index=None, header=True)
        return True

    def export_xml(self, export_type):
        # create the file structure
        xml_data = ET.Element('data')
        if int(export_type) == 2:
            for obj in self.data:
                items = ET.SubElement(xml_data, 'book')
                title = ET.SubElement(items, 'title')
                title.set('name', 'title')
                title.text = obj["title"]
        elif int(export_type) == 3:
            for obj in self.data:
                items = ET.SubElement(xml_data, 'book')
                author = ET.SubElement(items, 'author')
                author.set('name', 'author')
                author.text = obj["author"]
        else:
            for obj in self.data:
                items = ET.SubElement(xml_data, 'book')
                title = ET.SubElement(items, 'title')
                author = ET.SubElement(items, 'author')
                title.set('name', 'title')
                author.set('name', 'author')
                title.text = obj["title"]
                author.text = obj["author"]

        # create a new XML file with the results
        mydata = ET.tostring(xml_data)
        mydata = str(mydata, 'utf-8')
        myfile = open("static/export_data.xml", "w")
        myfile.write(mydata)
        return True


def fetch_all_titles():
    conn = sqlite3.connect('nlp_learn.db')

    # data = pd.read_csv('abcnews-date-text.csv', error_bad_lines=False);
    query = "SELECT id, title FROM books"
    result_set = conn.execute(query).fetchall()
    data = pd.DataFrame(result_set, columns=['id', 'title'])

    data_text = data[['title']]
    data_text['index'] = data_text.index
    return data_text


def lemmatize_stemming(text):
    stemmer = SnowballStemmer('english')
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))


def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 1:
            result.append(lemmatize_stemming(token))
    return result


def classify_book(title):
    """ Load existing trained model in lda_model variable """
    filename = "trained_model/lda_train_bow.model"
    lda_model = gensim.models.LdaModel.load(filename)

    documents = fetch_all_titles()
    processed_docs = documents['title'].map(preprocess)
    dictionary = gensim.corpora.Dictionary(processed_docs)
    dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)

    unseen_document = title
    bow_vector = dictionary.doc2bow(preprocess(unseen_document))
    """ Process of fetching one top 5 groups, with higher score """
    groups = []
    for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1 * tup[1]):
        groups.append(str(index))

    """ The topic IDs will be returned """
    return ", ".join(groups[:5])


def get_paginated_list(results, start, limit):
    start = int(start)
    limit = int(limit)
    count = len(results)
    if count < start or limit < 0:
        # abort(404)
        return {
            'start': start,
            'limit': limit,
            'total_records': count,
            'results': [],
            'total_pages': math.ceil(count / limit) if (count > 0) else 0
        }
    # make response
    obj = {
        'start': start,
        'limit': limit,
        'total_records': count,
        'results': results[((start - 1) * limit):(((start - 1) * limit) + limit)],
        'total_pages': math.ceil(count / limit) if (count > 0) else 0
    }
    return obj


def grouping_books(records=[]):
    temp = {}
    for row in records:
        groups = row["groups"].split(", ")
        for grp in groups:
            if grp not in temp:
                temp[grp] = 1
            else:
                temp[grp] += 1
    return temp

