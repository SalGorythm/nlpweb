import json
import sqlite3

conn = sqlite3.connect('nlp_learn.db')
f = open("goodreads_books.json", "r")
count = 0
res_counter = 0
for x in f:
    temp_d = json.loads(x)
    author = []
    if temp_d["authors"]:
        for auths in temp_d["authors"]:
            if auths["author_id"]:
                author_id = int(auths["author_id"])
                query = "SELECT author FROM authors where id={0}".format(author_id)
                result_set = conn.execute(query).fetchall()
                if result_set:
                    author.append(result_set[0][0])
    authors = ", ".join(author)
    query = "INSERT INTO books (title, author) VALUES ('{0}', '{1}')".format(temp_d["title"].replace("'", ""), authors)
    conn.execute(query)
    count += 1
    # print(count)
    # print(temp_d["title"])
    if count == 100:
        res_counter += count
        print("Commit on {0}".format(res_counter))
        count = 0
        conn.commit()

conn.commit()
conn.close()
print(res_counter)