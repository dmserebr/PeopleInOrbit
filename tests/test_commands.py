import os

import config
import db_access
import process_commands


class User:
    def __init__(self, id, first_name):
        self.id = id
        self.first_name = first_name


class Message:
    def __init__(self, from_user, text):
        self.from_user = from_user
        self.text = text


# integration test
def test_people_in_orbit():
    config.DB_FILENAME = 'test.db'
    os.remove(config.DB_FILENAME)
    db_access.init_sqlite()

    user_john = User(1, 'John')
    message1 = Message(user_john, '/peopleinorbit')
    message2 = Message(user_john, '/peopleinorbit')

    process_commands.process_people_in_orbit(message1)
    process_commands.process_people_in_orbit(message2)

    user_mark = User(2, 'Mark')
    message3 = Message(user_mark, '/peopleinorbit')

    process_commands.process_people_in_orbit(message3)

    queries = db_access.read_all_rows(table='queries')
    assert len(queries) == 3

    users = db_access.read_all_rows(table='users')
    assert len(users) == 2

    daily_data = db_access.read_all_rows(table='daily_data')
    assert len(daily_data) == 1

    interval_data = db_access.read_all_rows(table='interval_data')
    assert len(interval_data) == 3
