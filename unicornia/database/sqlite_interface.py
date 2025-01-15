"""
SQLite Interface Module

This module provides an interface to interact with an SQLite database.
It includes methods to connect to the database, create tables, insert data,
read data, and list all tables in the database.
"""

import sqlite3
from pathlib import Path


class SQLiteInterface:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.conn = self.connect_db()

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
        """Read data from the table."""
        sql = f"SELECT {columns} FROM {table} {where_clause}"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows

    def list_tables(self):
        """List all tables in the database."""
        sql = "SELECT name FROM sqlite_master WHERE type='table';"
        cur = self.conn.cursor()
        cur.execute(sql)
        tables = cur.fetchall()
        return [table[0] for table in tables]


# Example usage
if __name__ == "__main__":
    from pprint import pprint

    filepath = Path(__file__).parent / "_db" / "NadekoBot.db"
    db_interface = SQLiteInterface(filepath)

    tables = [
        "DiscordUser",
        "ShopEntry",
        "ShopEntryItem",
        "XPCurrencyReward",
        "XpRoleReward",
        "XpShopOwnedItem",
        "BankUsers",
        "Clubs",
    ]

    tables = db_interface.list_tables()
    pprint(tables)

    discord_users = db_interface.read_data("DiscordUser")
    pprint(discord_users[0])
