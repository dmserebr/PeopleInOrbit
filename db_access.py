import json
import logging
import sqlite3
from pathlib import Path

import config
from objects.astronauts_data import AstronautsData


def sqlite_connect():
    conn = sqlite3.connect(config.DB_FILENAME, check_same_thread=False)
    conn.execute("pragma journal_mode=wal;")
    return conn


def store_query(text, user_info, chat_id, response_data=None):
    conn = sqlite_connect()

    data = (
        text,
        user_info.id,
        json.dumps(user_info.__dict__),
        chat_id,
        None if response_data is None else json.dumps(response_data)
    )
    conn.execute('''INSERT INTO queries (query_name, user_id, user_info, chat_id, response_data)
        VALUES (?, ?, ?, ?, ?)''', data)
    conn.commit()
    conn.close()


def store_user(user_info, chat_id):
    conn = sqlite_connect()

    data = (
        user_info.id,
        json.dumps(user_info.__dict__),
        chat_id,
    )
    conn.execute('''INSERT INTO users (telegram_uid, user_info, chat_id)
        VALUES (?, ?, ?)
        ON CONFLICT(telegram_uid) DO UPDATE SET user_info = excluded.user_info, chat_id = excluded.chat_id''', data)
    conn.commit()
    conn.close()


def store_interval_data(payload):
    conn = sqlite_connect()
    payload_dump = json.dumps(payload.__dict__)
    conn.execute('''INSERT INTO interval_data (data) VALUES (?)''', (payload_dump,))
    conn.commit()
    conn.close()


def store_daily_data(payload):
    conn = sqlite_connect()
    payload_dump = json.dumps(payload.__dict__)
    conn.execute('''INSERT OR REPLACE INTO daily_data (day, data) VALUES (DATE('now'), ?)''', (payload_dump,))
    conn.commit()
    conn.close()


def store_data_with_ts(payload, ts):
    conn = sqlite_connect()
    payload_dump = json.dumps(payload.__dict__)
    conn.execute('''INSERT OR REPLACE INTO daily_data (day, data, update_ts) VALUES (?, ?, ?)''',
                 (ts.date(), payload_dump, ts))
    conn.execute('''INSERT INTO interval_data (interval_ts, data) VALUES (?, ?)''', (ts, payload_dump))
    conn.commit()
    conn.close()


def update_sent_updates(user_id):
    conn = sqlite_connect()

    try:
        conn.execute('''INSERT INTO sent_updates (user_id)
            VALUES (?)
            ON CONFLICT(user_id) DO UPDATE SET sent_update_ts = CURRENT_TIMESTAMP''', (user_id,))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        raise ex
    finally:
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
            chat_id INTEGER,
            response_data TEXT,
            query_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
    c.execute(
        '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            telegram_uid INTEGER NOT NULL,
            user_info TEXT,
            chat_id INTEGER,
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
    c.execute(
        '''CREATE TABLE IF NOT EXISTS sent_updates (
            user_id INTEGER REFERENCES user(id),
            sent_update_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT user_id_uniq UNIQUE (user_id)
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
        except Exception:
            logging.exception('Error when initializing database')
    except FileNotFoundError:
        logging.warning('Database not found, trying to create a new one')
        try:
            init_sqlite()
        except Exception:
            logging.exception('Error when creating database')
        else:
            logging.info('Successful created database')


def read_all_rows(table):
    conn = sqlite_connect()
    c = conn.cursor()

    c.execute('SELECT * FROM ' + table)

    rows = c.fetchall()
    conn.close()
    return rows


def get_valid_daily_data(exclude_today=False):
    conn = sqlite_connect()
    c = conn.cursor()

    sql = 'SELECT day, data FROM daily_data ' \
          'WHERE json_extract(data, \'$.astronauts\') IS NOT NULL ' \
          'AND json_extract(data, \'$.astronauts\') != \'[]\' {}' \
          'ORDER BY day DESC LIMIT 1' \
        .format('AND day < DATE(\'now\') ' if exclude_today else '')
    c.execute(sql)

    row = c.fetchone()
    conn.close()

    if not row:
        logging.error('Error: no daily data exists')
        return None, None

    try:
        astronauts_data_json = json.loads(row[1])
        return row[0], AstronautsData(**astronauts_data_json)
    except Exception:
        logging.exception('Error when parsing JSON')
        return None, None


def get_users_to_send_updates():
    conn = sqlite_connect()
    c = conn.cursor()

    c.execute(
        '''SELECT u.id, u.telegram_uid, u.chat_id
            FROM users u 
            LEFT JOIN sent_updates s ON u.id = s.user_id 
            WHERE s.sent_update_ts < DATE('now') OR s.sent_update_ts IS NULL''')

    rows = c.fetchall()
    conn.close()
    return rows
