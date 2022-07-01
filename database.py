"""
database.py

Request's word list from sqlite database
"""
from re import T
import sqlite3
import os

DATABASE_NAME = "./database.db"

def get_mp3s_from_wordlist(words):
    """requests mp3s from database and loads from file system

    Args:
        words (list): a list of words in a sentence
    """
    
    tuple_of_words = [(word,) for word in words]

    with Database(DATABASE_NAME) as db:
        db.cursor.executemany("SELECT path FROM word_list WHERE word=?", tuple_of_words)

        for word in words:
            r = db.cursor.fetchone()

            if r is None:
                print(f"No sound found for word: {word}")
                continue

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
        conn.close()

    def __enter__(self):
        self.connection: sqlite3.Connection = sqlite3.connect(self.db_file)
        self.connection.row_factory = sqlite3.Row
        self.cursor: sqlite3.Cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()
    
    def migrate(self, conn: sqlite3.Connection):
        """
        run though sql migrations
        """
        # for file in migrations
        path_to_migrations  = f"{os.path.dirname(__file__)}/migrations/"

        for file in os.listdir(path_to_migrations):
            if file.endswith(".sql"):
                # open file
                with open(path_to_migrations + file, 'r') as f:
                    # execute sql
                    conn.executescript(f.read())
                    # commit changes
                    conn.commit()
