import logging

import firebase_admin
import firebase_admin.messaging
from firebase_admin import credentials
from firebase_admin.messaging import Message, Notification

is_initialized = False


def init_client(config_path):
    global is_initialized

    cred = credentials.Certificate(config_path)
    app = firebase_admin.initialize_app(cred)
    logging.info(f'Firebase app {app} is initialized')
    is_initialized = True


def send_push_notifications(notifications):
    global is_initialized  # noqa: F824

    if not is_initialized:
        logging.warning('Firebase app is not initialized! Skipping notifications!')
        return

    messages = [Message(
        topic='people_in_orbit',
        notification=Notification(title=notification['title'], body=notification['description'])
    ) for notification in notifications]

    firebase_admin.messaging.send_all(messages)
    logging.info(f'Sent {len(messages)} messages to Firebase')
