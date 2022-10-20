import json
import sqlite3
from pathlib import Path


def sqlite_connect():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    conn.execute("pragma journal_mode=wal;")
    return conn


def store_query(message, response_data=None):
    conn = sqlite_connect()

    data = (
        message.text,
        message.from_user.id,
        json.dumps(message.from_user.__dict__),
        None if response_data is None else json.dumps(response_data)
    )
    conn.execute('''INSERT INTO queries (query_name, user_id, user_info, response_data)
        VALUES (?, ?, ?, ?)''', data)
    conn.commit()
    conn.close()


def init_sqlite():
    conn = sqlite_connect()
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE queries (
            id INTEGER PRIMARY KEY,
            query_name TEXT,
            user_id INTEGER,
            user_info TEXT,
            response_data TEXT,
            query_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
    conn.commit()
    conn.close()
    return


def check_sqlite_exists():
    db = Path("./database.db")
    try:
        db.resolve(strict=True)
    except FileNotFoundError:
        print("Database not found, trying to create a new one")
        try:
            init_sqlite()
        except Exception as e:
            print("Error when creating database: ", e.__repr__(), e.args)
            pass
        else:
            print("Successful created database")
