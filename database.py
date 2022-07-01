"""
database.py

Request's word list from sqlite database
"""
import sqlite3
import os

def get_mp3s_from_wordlist(words):
    """requests mp3s from database and loads from file system

    Args:
        words (list): a list of words in a sentence
    """


"""
use case:

with Database('db_file') as db:
    db.cursor.execute("SELECT * FROM table")
    for row in db.cursor:
        print(row)
"""
# Sqlite3 database
# https://www.sqlite.org/lang.html
class Database:
    """
    boiler plate sqlite3 context handler
    """
    def __init__(self, db_file):
        self.db_file = db_file
        # run sql migrations
        conn = sqlite3.connect(self.db_file)
        self.migrate(conn)

    def __enter__(self):
        self.connection: sqlite3.Connection = sqlite3.connect(self.db_file)
        self.connection.row_factory = sqlite3.Row
        self.cursor: sqlite3.Cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()
    
    def migrate(conn: sqlite3.Connection):
        """
        run though sql migrations
        """
        # for file in migrations
        for file in os.listdir(f"{os.path.dirname(__file__)}/migrations"):
            if file.endswith(".sql"):
                # open file
                with open(file, 'r') as f:
                    # execute sql
                    conn.executescript(f.read())
                    # commit changes
                    conn.commit()
