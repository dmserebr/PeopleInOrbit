import json
import os
from datetime import date, datetime
from pathlib import Path
from unittest.mock import call

import pytest

import config
import db_access
import updater_thread

CURRENT_DIR = Path(__file__).parent


class User:
    def __init__(self, id, first_name):
        self.id = id
        self.first_name = first_name


class Chat:
    def __init__(self, id):
        self.id = id


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


def load_resource(resource_name):
    return open(CURRENT_DIR / 'resources' / resource_name, encoding='utf-8').read()


def test_updater_if_no_data(mocker):
    mocker.patch.object(updater_thread, 'get_astronauts_data', return_value=[])
    mocker.patch.object(updater_thread.send_messages.bot, 'send_message')
    db_access.store_user(User(1, 'John'), 10)

    updater_thread.process_updates()

    daily_data_after = db_access.read_all_rows('daily_data')
    assert len(daily_data_after) == 1
    assert daily_data_after[0][0] == date.today().strftime('%Y-%m-%d')
    assert daily_data_after[0][1] == '{"astronauts": []}'

    users_after = db_access.read_all_rows('users')
    assert len(users_after) == 1

    updater_thread.send_messages.bot.send_message.assert_not_called()


def test_updater_if_data_different(mocker):
    test_start_ts = datetime.utcnow().replace(microsecond=0)  # CURRENT_TIMESTAMP in SQLite is in UTC without millis

    astronauts_data = json.loads(load_resource('test_astronauts_data.json'))
    data_for_today = astronauts_data[:-2]
    data_for_yesterday = astronauts_data[1:]

    mocker.patch.object(updater_thread, 'get_astronauts_data', return_value=data_for_today)
    mocker.patch.object(updater_thread.send_messages.bot, 'send_message')
    db_access.store_user(User(1, 'John'), 10)

    db_access.store_data_with_ts({'astronauts': data_for_yesterday}, datetime.strptime('2022-12-15', '%Y-%m-%d'))

    updater_thread.process_updates()

    final_daily_data = db_access.read_all_rows('daily_data')
    assert len(final_daily_data) == 2
    assert final_daily_data[0][0] == '2022-12-15'
    assert final_daily_data[0][1] == '{"astronauts": ' + json.dumps(data_for_yesterday) + '}'
    assert final_daily_data[0][2] == '2022-12-15 00:00:00'
    assert final_daily_data[1][0] == date.today().strftime('%Y-%m-%d')
    assert final_daily_data[1][1] == '{"astronauts": ' + json.dumps(data_for_today) + '}'
    assert datetime.strptime(final_daily_data[1][2], '%Y-%m-%d %H:%M:%S') >= test_start_ts

    final_interval_data = db_access.read_all_rows('interval_data')
    assert len(final_interval_data) == 2
    assert final_interval_data[0][1] == '2022-12-15 00:00:00'
    assert final_interval_data[0][2] == '{"astronauts": ' + json.dumps(data_for_yesterday) + '}'
    assert datetime.strptime(final_interval_data[1][1], '%Y-%m-%d %H:%M:%S') >= test_start_ts
    assert final_interval_data[1][2] == '{"astronauts": ' + json.dumps(data_for_today) + '}'

    expected_added_message = load_resource('message_added_data_different.txt')
    expected_removed_message = load_resource('message_removed_data_different.txt')

    updater_thread.send_messages.bot.send_message.assert_has_calls([
        call(10, expected_added_message),
        call(10, expected_removed_message)
    ])
