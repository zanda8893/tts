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
        # get migration version
        path_to_migrations  = f"{os.path.dirname(__file__)}/migrations/"
        version: int

        try:
            version = conn.execute("SELECT version FROM meta").fetchone()[0]
        except sqlite3.OperationalError or sqlite3.OperationalError:
            version = -1
        
        schema_version = len(os.listdir(path_to_migrations)) - 1

        while version < schema_version:
            version += 1
            with open(f"{path_to_migrations}v{version}.sql", "r") as f:
                sql = f.read()
                conn.executescript(sql)
            
            conn.commit()
            
