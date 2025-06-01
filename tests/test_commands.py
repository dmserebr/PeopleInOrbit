import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest

import config
import db_access
import http_data_loader
import process_commands
from objects.astronauts_data import AstronautsData

CURRENT_DIR = Path(__file__).parent


# Integration test (performs real HTTP calls)


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

    yield

    cleanup_test_db()


def cleanup_test_db():
    config.DB_FILENAME = 'test.db'
    if os.path.exists(config.DB_FILENAME):
        os.remove(config.DB_FILENAME)
    db_access.init_sqlite()


def test_people_in_orbit():
    user_john = User(1, 'John')
    chat_john = Chat(1)
    message1 = Message(user_john, chat_john, '/peopleinorbit')
    message2 = Message(user_john, chat_john, '/peopleinorbit')

    process_commands.process_people_in_orbit(message1)
    process_commands.process_people_in_orbit(message2)

    user_mark = User(2, 'Mark')
    chat_mark = Chat(2)
    message3 = Message(user_mark, chat_mark, '/peopleinorbit')

    process_commands.process_people_in_orbit(message3)

    queries = db_access.read_all_rows(table='queries')
    assert len(queries) == 3

    users = db_access.read_all_rows(table='users')
    assert len(users) == 2

    daily_data = db_access.read_all_rows(table='daily_data')
    assert len(daily_data) == 1

    interval_data = db_access.read_all_rows(table='interval_data')
    assert len(interval_data) == 3

    day, last_daily_data = db_access.get_valid_daily_data()
    assert last_daily_data is not None
    assert last_daily_data.is_valid
    assert len(last_daily_data.astronauts) > 0
    first_astronaut = last_daily_data.astronauts[0]
    assert first_astronaut['name']
    assert first_astronaut['country']


def test_people_in_orbit_if_has_data():
    data_for_yesterday = json.loads(load_resource('test_astronauts_data.json'))
    db_access.store_data_with_ts(AstronautsData(data_for_yesterday, True), datetime.utcnow() - timedelta(days=1))

    user_john = User(1, 'John')
    chat_john = Chat(1)
    message1 = Message(user_john, chat_john, '/peopleinorbit')
    message2 = Message(user_john, chat_john, '/peopleinorbit')

    process_commands.process_people_in_orbit(message1)
    process_commands.process_people_in_orbit(message2)

    queries = db_access.read_all_rows(table='queries')
    assert len(queries) == 2

    users = db_access.read_all_rows(table='users')
    assert len(users) == 1

    daily_data = db_access.read_all_rows(table='daily_data')
    assert len(daily_data) == 1

    interval_data = db_access.read_all_rows(table='interval_data')
    assert len(interval_data) == 3

    day, last_daily_data = db_access.get_valid_daily_data()
    assert last_daily_data is not None
    assert last_daily_data.is_valid
    assert last_daily_data.astronauts == data_for_yesterday


def test_people_in_orbit_if_network_error(mocker):
    user_john = User(1, 'John')
    chat_john = Chat(1)
    message1 = Message(user_john, chat_john, '/peopleinorbit')

    mocker.patch.object(http_data_loader, 'load_astronauts', side_effect=Exception('Network error'))

    process_commands.process_people_in_orbit(message1)

    queries = db_access.read_all_rows(table='queries')
    assert len(queries) == 1

    users = db_access.read_all_rows(table='users')
    assert len(users) == 1

    daily_data = db_access.read_all_rows(table='daily_data')
    assert len(daily_data) == 1

    interval_data = db_access.read_all_rows(table='interval_data')
    assert len(interval_data) == 1

    day, last_daily_data = db_access.get_valid_daily_data()
    assert last_daily_data is None


def load_resource(resource_name):
    return open(CURRENT_DIR / 'resources' / resource_name, encoding='utf-8').read()
