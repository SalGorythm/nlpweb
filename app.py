import gensim

import nltk
from flask import Flask, request, render_template, send_file
from service import Books, ExportData, classify_book, fetch_all_titles, preprocess, \
    get_paginated_list, grouping_books
from models import Schema
from helper import json_error, json_success, validation_errors
import sqlite3
import numpy as np

import json

app = Flask(__name__)


@app.route("/books", methods=["GET"])
# description="Index page, will list the books and on top will be a form to add new books"
def list_books():
    try:
        books_list = Books().list()
        # books_list = get_paginated_list(books_list, start=1, limit=10)
        return render_template("index.html", results={"data": books_list, "suggestion_flag": False,
                                                      "suggested_books": []})
    except Exception as e:
        return json_error(message=str(e))


@app.route("/books", methods=["POST"])
# description="New books will be added using this URL"
def add_book():
    try:
        params = request.get_json()
        if not params:
            params = request.form

        if not params.get("title") or not params.get("author"):
            return validation_errors(errors="title and author is required")

        groups = classify_book(params["title"])
        temp_params = {"title": request.form["title"], "author": request.form["author"], "groups": groups}
        books_list = Books().create(temp_params)
        suggested_books = Books().list_books_in_group(groups.split(", ")[0])
        return render_template("index.html", results={"data": books_list,
                                                      "suggestion_flag": True,
                                                      "suggested_books": suggested_books})
    except Exception as e:
        return json_error(message=str(e))


@app.route("/groups", methods=["GET"])
# description="New books will be added using this URL"
def get_group_wise_books():
    try:
        books_list = Books().list()
        data = grouping_books(books_list)
        records = []
        groups = data.keys()
        for grp in groups:
            temp = {"groups": int(grp), "books_count": data[grp]}
            records.append(temp)
        if records:
            records = sorted(records, key=lambda i: i['books_count'], reverse=True)
        return render_template("groups.html", results=records)
    except Exception as e:
        return json_error(message=str(e))


@app.route("/books/<item_id>", methods=["DELETE", "POST", "GET"])
# description="A title will be removed from the database, the status will be set to 0"
def delete_book(item_id):
    try:
        books_list = Books().delete(item_id)
        # return list_books()
        return render_template("index.html", results={"data": books_list, "suggestion_flag": False,
                                                      "suggested_books": []})
        # return json_success(results=books_list)
    except Exception as e:
        return json_error(message=str(e))


@app.route("/export-excel/<export_type>", methods=["GET"])
# description="This URL will export excel data"
def export_excel(export_type):
    ExportData().export_csv(export_type)
    return send_file("static/export_data.csv", as_attachment=True, attachment_filename="books_data.csv")


@app.route("/export-xml/<export_type>", methods=["GET"])
# description="This URL will export XML data"
def export_xml(export_type):
    ExportData().export_xml(export_type)
    # return send_from_directory(directory="static/", filename="export_data.xml")
    return send_file("static/export_data.xml", as_attachment=True, attachment_filename="books_data.xml")


@app.route("/train-model", methods=["GET"])
# description="Training for classifying book on titles"
def train_book_model():

    """ Fetching all the documnets i.e. book titles  - Start """
    documents = fetch_all_titles()
    """ Fetching all the documnets i.e. book titles - Complete"""

    np.random.seed(2018)

    """ Downloading package wordnet  - Start"""
    nltk.download('wordnet')
    """ Downloading package wordnet - Complete """

    processed_docs = documents['title'].map(preprocess)
    dictionary = gensim.corpora.Dictionary(processed_docs)
    dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)
    bow_docs = [dictionary.doc2bow(doc) for doc in processed_docs]

    """ Running LDA using Bag of Words """
    lda_model = gensim.models.LdaMulticore(bow_docs, num_topics=25, id2word=dictionary, passes=2, workers=2)
    lda_model.save('trained_model/lda_train_bow.model')
    """ LDA Training - Complete """

    return json_success(results="Training Complete, files saved!")


@app.route("/add-static-data", methods=["GET"])
def add_new_book():
    filename = "books_2.json"
    temp = {}
    with open(filename, 'r') as json_data:
        # print(type(f))
        temp = json.load(json_data)

    counter = 0
    for obj in temp:
        # print(obj["authors"])
        # params = {"title": obj["title"], "author": ", ".join(obj["authors"])}
        books_list = Books().create(obj)
        counter += 1

    return json_success(results=counter)


@app.route("/add-authors", methods=["GET"])
def add_authors():
    conn = sqlite3.connect('nlp_learn.db')
    filename = "goodreads_book_authors.json"
    temp = {}
    with open(filename, 'r') as json_data:
        # print(type(json_data))
        # jsonn = json.dump(json_data)
        temp = json.load(json_data)

    commit_counter = 0
    total_data_count = 0
    for row in temp:
        query = "INSERT INTO authors VALUES ({0}, '{1}')".format(int(row["author_id"]), row["name"].replace("'", ""))
        print(query)
        conn.execute(query)
        commit_counter += 1
        if commit_counter == 1000:
            total_data_count += commit_counter
            commit_counter = 0
            conn.commit()

    conn.commit()
    conn.close()

    return json_success(results=total_data_count)


if __name__ == "__main__":
    try:
        Schema()
    except Exception as e:
        print(str(e))
    app.run(debug=True, port=5000)
