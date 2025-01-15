"""
SQLite Interface Module

This module provides an interface to interact with an SQLite database.
It includes methods to connect to the database, create tables, insert data,
read data, and list all tables in the database.
"""

import sqlite3
from pathlib import Path


class DBInterface:
    def __init__(self, filepath: Path, tables_data_classes: list):
        self.filepath = filepath
        self.tables_data_classes = tables_data_classes

        self.conn = self.connect_db()
        self.load_all_table_data()

    def load_all_table_data(self):
        """Load data from all tables and store in a dictionary."""
        for table in self.tables_data_classes.keys():
            data = self.read_data(table)
            setattr(self, table, data)

    def connect_db(self):
        """Connect to the SQLite database."""
        conn = sqlite3.connect(self.filepath)
        return conn

    def create_table(self, create_table_sql):
        """Create a table from the create_table_sql statement."""
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except sqlite3.Error as e:
            print(e)

    def insert_data(self, table, data):
        """Insert data into the table."""
        keys = ", ".join(data.keys())
        question_marks = ", ".join(["?"] * len(data))
        values = tuple(data.values())

        sql = f"INSERT INTO {table} ({keys}) VALUES ({question_marks})"
        cur = self.conn.cursor()
        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid

    def read_data(self, table, columns="*", where_clause=""):
        """Read data from the table and return as a list of dictionaries."""
        sql = f"SELECT {columns} FROM {table} {where_clause}"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        column_names = [description[0] for description in cur.description]
        result = [dict(zip(column_names, row)) for row in rows]
        return result

    def list_tables(self):
        """List all tables in the database."""
        sql = "SELECT name FROM sqlite_master WHERE type='table';"
        cur = self.conn.cursor()
        cur.execute(sql)
        tables = cur.fetchall()
        return [table[0] for table in tables]
