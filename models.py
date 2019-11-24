import sqlite3
from helper import json_error


class Schema:
    def __init__(self):
        self.conn = sqlite3.connect('nlp_learn.db')
        self.create_books_table()

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def create_books_table(self):

        query = """
            CREATE TABLE IF NOT EXISTS "books" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                is_deleted boolean DEFAULT 0,
                groups INTEGER default null,
                created_on Date DEFAULT CURRENT_DATE
            );
        """
        self.conn.execute(query)


class BooksModel:
    __table_name__ = "books"

    def __init__(self):
        self.conn = sqlite3.connect('nlp_learn.db')
        self.conn.row_factory = sqlite3.Row

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def create(self, params):
        try:
            query = """ INSERT into {0} (title, author, groups)
                        VALUES ("{1}","{2}", "{3}")
                    """.format(self.__table_name__, params.get("title"), params.get("author"), params.get("groups"))
            self.conn.execute(query)
            return self.list_items()
        except Exception as e:
            return json_error(message=str(e))

    def delete(self, item_id):
        try:
            query = """ UPDATE {0} 
                        SET is_deleted =  {1} 
                        WHERE id = {2}
                    """.format(self.__table_name__, 1, item_id)
            if self.conn.execute(query):
                return self.list_items()
            else:
                return False
        except Exception as e:
            return json_error(message=str(e))

    def list_items(self):
        query = """ SELECT id, title, author, groups, created_on 
                    FROM {0} 
                    WHERE is_deleted=0
                    limit 3000
                """.format(self.__table_name__)
        result_set = self.conn.execute(query).fetchall()
        result = [{column: row[i]
                  for i, column in enumerate(result_set[0].keys())}
                  for row in result_set]
        return result

    def list_books_in_group(self, group):
        query = """ SELECT id, title, author, groups, created_on 
                            FROM {0} 
                            WHERE groups like "{1}"
                            limit 10
                        """.format(self.__table_name__, group)
        result_set = self.conn.execute(query).fetchall()
        result = [{column: row[i]
                   for i, column in enumerate(result_set[0].keys())}
                  for row in result_set]
        return result

