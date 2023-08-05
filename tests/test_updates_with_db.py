import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import call

import pytest

import config
import db_access
import process_commands
import updater_thread
from objects.astronauts_data import AstronautsData

CURRENT_DIR = Path(__file__).parent


class User:
    def __init__(self, id, first_name):
        self.id = id
        self.first_name = first_name


class Chat:
    def __init__(self, id):
        self.id = id


class Message:
    def __init__(self, from_user, chat, text):
        self.from_user = from_user
        self.chat = chat
        self.text = text


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    cleanup_test_db()
    config.FIREBASE_NOTIFICATIONS_ENABLED = False

    yield

    cleanup_test_db()


def cleanup_test_db():
    config.DB_FILENAME = 'test.db'
    if os.path.exists(config.DB_FILENAME):
        os.remove(config.DB_FILENAME)
    db_access.init_sqlite()


def load_resource(resource_name):
    return open(CURRENT_DIR / 'resources' / resource_name, encoding='utf-8').read()


def test_updater_if_no_data(mocker):
    mocker.patch.object(updater_thread, 'get_astronauts_data', return_value=AstronautsData())
    mocker.patch.object(updater_thread.send_messages.bot, 'send_message')
    db_access.store_user(User(1, 'John'), 10)

    updater_thread.process_updates()

    daily_data_after = db_access.read_all_rows('daily_data')
    assert len(daily_data_after) == 1
    assert daily_data_after[0][0] == datetime.strftime(datetime.utcnow().date(), '%Y-%m-%d')
    assert daily_data_after[0][1] == '{"astronauts": [], "is_valid": false}'

    users_after = db_access.read_all_rows('users')
    assert len(users_after) == 1

    updater_thread.send_messages.bot.send_message.assert_not_called()


def test_updater_if_data_different(mocker):
    test_start_ts = datetime.utcnow().replace(microsecond=0)  # CURRENT_TIMESTAMP in SQLite is in UTC without millis

    astronauts_data = json.loads(load_resource('test_astronauts_data.json'))
    data_for_today = AstronautsData(**astronauts_data)
    data_for_today.astronauts = data_for_today.astronauts[:-2]
    data_for_yesterday = AstronautsData(**astronauts_data)
    data_for_yesterday.astronauts = data_for_yesterday.astronauts[1:]

    mocker.patch.object(updater_thread, 'get_astronauts_data', return_value=data_for_today)
    mocker.patch.object(updater_thread.send_messages.bot, 'send_message')
    db_access.store_user(User(1, 'John'), 10)

    db_access.store_data_with_ts(data_for_yesterday, datetime.strptime('2022-12-15', '%Y-%m-%d'))

    updater_thread.process_updates()

    final_daily_data = db_access.read_all_rows('daily_data')
    assert len(final_daily_data) == 2
    assert final_daily_data[0][0] == '2022-12-15'
    assert final_daily_data[0][1] == json.dumps(data_for_yesterday.__dict__)
    assert final_daily_data[0][2] == '2022-12-15 00:00:00'
    assert final_daily_data[1][0] == datetime.strftime(datetime.utcnow().date(), '%Y-%m-%d')
    assert final_daily_data[1][1] == json.dumps(data_for_today.__dict__)
    assert datetime.strptime(final_daily_data[1][2], '%Y-%m-%d %H:%M:%S') >= test_start_ts

    final_interval_data = db_access.read_all_rows('interval_data')
    assert len(final_interval_data) == 2
    assert final_interval_data[0][1] == '2022-12-15 00:00:00'
    assert final_interval_data[0][2] == json.dumps(data_for_yesterday.__dict__)
    assert datetime.strptime(final_interval_data[1][1], '%Y-%m-%d %H:%M:%S') >= test_start_ts
    assert final_interval_data[1][2] == json.dumps(data_for_today.__dict__)

    expected_added_message = load_resource('message_added_data_different.txt')
    expected_removed_message = load_resource('message_removed_data_different.txt')

    updater_thread.send_messages.bot.send_message.assert_has_calls([
        call(10, expected_added_message),
        call(10, expected_removed_message)
    ])


def test_updater_if_command_called_between_daily_updates(mocker):
    # 0. first day - updater sets daily data
    # 1. data changes
    # 2. user arrives - daily data is updated
    # 3. next day - compare with daily data, change is not caught

    utcnow = datetime.utcnow()

    def mock_date_tomorrow(*_):
        return datetime.strftime(utcnow.date() + timedelta(days=1), '%Y-%m-%d')

    def mock_ts_tomorrow(*_):
        return datetime.strftime(utcnow + timedelta(days=1), '%Y-%m-%d %H:%M:%S.%f')

    def mock_sqlite3_connect():
        conn = sqlite3.connect(config.DB_FILENAME, check_same_thread=False)
        conn.create_function('DATE', -1, mock_date_tomorrow)
        conn.create_function('CURRENT_TIMESTAMP', 0, mock_ts_tomorrow)
        return conn

    astronauts_data = json.loads(load_resource('test_astronauts_data.json'))
    data_for_today = AstronautsData(**astronauts_data)
    data_for_today.astronauts = data_for_today.astronauts[:-2]

    data_for_yesterday = AstronautsData(**astronauts_data)
    data_for_yesterday.astronauts = data_for_yesterday.astronauts[1:]

    mocker.patch.object(updater_thread.send_messages.bot, 'send_message')
    user = User(1, 'John')
    chat = Chat(10)
    db_access.store_user(user, chat.id)

    # store 'old' data for today (1 hour before)
    db_access.store_data_with_ts(data_for_yesterday, utcnow - timedelta(hours=1))

    # command with fetches new data on the same day
    mocker.patch.object(process_commands.content_generator, 'get_people_in_orbit',
                        return_value=(None, data_for_today.astronauts))
    process_commands.process_people_in_orbit(Message(user, chat, '/peopleinorbit'))

    # imitate call for tomorrow
    mocker.patch.object(updater_thread, 'get_astronauts_data', return_value=data_for_today)
    mocker.patch.object(db_access, 'sqlite_connect', side_effect=mock_sqlite3_connect)
    updater_thread.process_updates()

    final_daily_data = db_access.read_all_rows('daily_data')
    assert len(final_daily_data) == 2
    assert final_daily_data[0][0] == datetime.strftime(utcnow.date(), '%Y-%m-%d')
    assert final_daily_data[0][1] == json.dumps(data_for_yesterday.__dict__)
    assert final_daily_data[0][2] == datetime.strftime(utcnow - timedelta(hours=1), '%Y-%m-%d %H:%M:%S.%f')
    assert final_daily_data[1][0] == datetime.strftime(utcnow.date() + timedelta(days=1), '%Y-%m-%d')
    assert final_daily_data[1][1] == json.dumps(data_for_today.__dict__)
    assert final_daily_data[1][2] == datetime.strftime(utcnow + timedelta(days=1), '%Y-%m-%d %H:%M:%S.%f')

    final_interval_data = db_access.read_all_rows('interval_data')
    assert len(final_interval_data) == 3
    assert final_interval_data[0][1] == datetime.strftime(utcnow - timedelta(hours=1), '%Y-%m-%d %H:%M:%S.%f')
    assert final_interval_data[0][2] == json.dumps(data_for_yesterday.__dict__)
    assert datetime.strptime(final_interval_data[1][1], '%Y-%m-%d %H:%M:%S') >= utcnow.replace(microsecond=0)
    assert final_interval_data[1][2] == json.dumps(data_for_today.__dict__)
    assert final_interval_data[2][1] == datetime.strftime(utcnow + timedelta(days=1), '%Y-%m-%d %H:%M:%S.%f')
    assert final_interval_data[2][2] == json.dumps(data_for_today.__dict__)

    expected_added_message = load_resource('message_added_data_different.txt')
    expected_removed_message = load_resource('message_removed_data_different.txt')

    updater_thread.send_messages.bot.send_message.assert_has_calls([
        call(10, expected_added_message),
        call(10, expected_removed_message)
    ])
