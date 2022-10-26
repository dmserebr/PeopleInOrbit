import json
import sqlite3
from pathlib import Path

import config


def sqlite_connect():
    conn = sqlite3.connect(config.DB_FILENAME, check_same_thread=False)
    conn.execute("pragma journal_mode=wal;")
    return conn


def store_query(text, user_info, response_data=None):
    conn = sqlite_connect()

    data = (
        text,
        user_info.id,
        json.dumps(user_info.__dict__),
        None if response_data is None else json.dumps(response_data)
    )
    conn.execute('''INSERT INTO queries (query_name, user_id, user_info, response_data)
        VALUES (?, ?, ?, ?)''', data)
    conn.commit()
    conn.close()


def store_user(user_info):
    conn = sqlite_connect()

    data = (
        user_info.id,
        json.dumps(user_info.__dict__),
    )
    conn.execute('''INSERT INTO users (telegram_uid, user_info)
        VALUES (?, ?)
        ON CONFLICT(telegram_uid) DO UPDATE SET user_info = excluded.user_info''', data)
    conn.commit()
    conn.close()


def store_data(payload):
    conn = sqlite_connect()
    payload_dump = json.dumps(payload)
    conn.execute('''INSERT OR REPLACE INTO daily_data (day, data) VALUES (DATE('now'), ?)''', (payload_dump,))
    conn.execute('''INSERT INTO interval_data (data) VALUES (?)''', (payload_dump,))
    conn.commit()
    conn.close()


def init_sqlite():
    conn = sqlite_connect()
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY,
            query_name TEXT,
            user_id INTEGER,
            user_info TEXT,
            response_data TEXT,
            query_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
    c.execute(
        '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            telegram_uid INTEGER NOT NULL,
            user_info TEXT,
            update_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT telegram_uid_uniq UNIQUE (telegram_uid)
        )''')
    c.execute(
        '''CREATE TABLE IF NOT EXISTS daily_data (
            day DATE PRIMARY KEY,
            data TEXT,
            update_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')  # insert into daily_data (day,data) values (date('now'),'test2');
    c.execute(
        '''CREATE TABLE IF NOT EXISTS interval_data (
            id INTEGER PRIMARY KEY,
            interval_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data TEXT
        )''')
    conn.commit()
    conn.close()
    return


def check_sqlite_exists():
    db = Path("./" + config.DB_FILENAME)
    try:
        db.resolve(strict=True)
        try:
            init_sqlite()  # hack until versioned migrations are supported
        except Exception as e:
            print("Error when initializing database: ", e.__repr__(), e.args)
            pass
    except FileNotFoundError:
        print("Database not found, trying to create a new one")
        try:
            init_sqlite()
        except Exception as e:
            print("Error when creating database: ", e.__repr__(), e.args)
            pass
        else:
            print("Successful created database")


def read_all_rows(table):
    conn = sqlite_connect()
    c = conn.cursor()

    c.execute('SELECT * FROM ' + table)

    rows = c.fetchall()
    conn.close()
    return rows
