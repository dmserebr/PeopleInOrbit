import json
import os
from pathlib import Path
from unittest.mock import call

import pytest

import config
import db_access
import updater_thread

CURRENT_DIR = Path(__file__).parent


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
    mocker.patch.object(db_access, 'get_users_to_send_updates', return_value=[(1, 1, None)])

    updater_thread.process_updates()

    updater_thread.send_messages.bot.send_message.assert_not_called()


def test_updater_if_no_previous_data(mocker):
    mocker.patch.object(updater_thread, 'get_astronauts_data',
                        return_value=json.loads(load_resource('test_astronauts_data.json')))
    mocker.patch.object(updater_thread.send_messages.bot, 'send_message')
    mocker.patch.object(db_access, 'get_users_to_send_updates', return_value=[(1, 1, None)])

    updater_thread.process_updates()

    expected_message = load_resource('message_added.txt')
    updater_thread.send_messages.bot.send_message.assert_called_once_with(1, expected_message)


def test_updater_if_new_data_same_as_previous(mocker):
    test_astronauts_data = json.loads(load_resource('test_astronauts_data.json'))
    mocker.patch.object(updater_thread, 'get_astronauts_data', return_value=test_astronauts_data)
    mocker.patch.object(db_access, 'get_daily_data', return_value={'astronauts': test_astronauts_data})
    mocker.patch.object(updater_thread.send_messages.bot, 'send_message')
    mocker.patch.object(db_access, 'get_users_to_send_updates', return_value=[(1, 1, None)])

    updater_thread.process_updates()

    updater_thread.send_messages.bot.send_message.assert_not_called()


def test_updater_if_data_is_different(mocker):
    astronauts_data = json.loads(load_resource('test_astronauts_data.json'))
    data_for_today = astronauts_data[:-2]
    data_for_yesterday = astronauts_data[1:]

    mocker.patch.object(updater_thread, 'get_astronauts_data', return_value=data_for_today)
    mocker.patch.object(db_access, 'get_daily_data', return_value={'astronauts': data_for_yesterday})
    mocker.patch.object(updater_thread.send_messages.bot, 'send_message')
    mocker.patch.object(db_access, 'get_users_to_send_updates', return_value=[(1, 1, None)])

    updater_thread.process_updates()

    expected_added_message = load_resource('message_added_data_different.txt')
    expected_removed_message = load_resource('message_removed_data_different.txt')
    updater_thread.send_messages.bot.send_message.assert_has_calls([
        call(1, expected_added_message),
        call(1, expected_removed_message)
    ])
