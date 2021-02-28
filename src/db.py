import os
import sqlite3

class DB:
    def __init__(self):
        self.__conn = sqlite3.connect("vinyl.db")
        self.__cur = self.__conn.cursor()

    def __scheme(self):
        scheme_collection = """CREATE TABLE collection (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        artist TEXT NOT NULL,
        title TEXT NOT NULL,
        year INTEGER NOT NULL,
        master_id INTEGER NOT NULL)"""

        scheme_master = """CREATE TABLE master (
        master_id INTERGER PRIMARY KEY NOT NULL,
        year INTEGER NOT NULL)"""

        self.__cur.execute(scheme_collection)
        self.__cur.execute(scheme_master)
        self.__conn.commit()
    
    def insert(self, args):
        self.__cur.execute("")

    def close(self):
        self.__conn.close()
