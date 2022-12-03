import logging
import threading
import time

import schedule

import config
import db_access
import http_data_loader
import send_messages
import wiki_parser


def process_updates():
    logging.info('Updating astronaut data according to schedule')
    astronauts_data = None
    try:
        page_soup = http_data_loader.load_astronauts()
        astronauts_data = wiki_parser.get_astronauts(page_soup)
    except Exception:
        logging.exception('Error while updating astronauts data')

    astronauts_data_for_yesterday = db_access.get_daily_data(exclude_today=True)['astronauts']

    db_access.store_data({'astronauts': astronauts_data})

    # send updates
    updates = calculate_updates(astronauts_data, astronauts_data_for_yesterday)
    if updates:
        logging.info('Sending updates to all users')
        send_messages.send_updates_to_all_users(updates)


def calculate_updates(data, data_for_yesterday):
    names_today = [astronaut['name'] for astronaut in data]
    names_yesterday = [astronaut['name'] for astronaut in data_for_yesterday]

    added = [astronaut for astronaut in data if not astronaut['name'] in names_yesterday]
    removed = [astronaut for astronaut in data_for_yesterday if not astronaut['name'] in names_today]

    if added + removed:
        return {'added': added, 'removed': removed}
    else:
        return None


def init_jobs():
    schedule.every().day.at(config.UPDATER_START_TIME).do(process_updates).tag('process_updates')


class UpdaterThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'UpdaterThread'
        self.daemon = True

    def run(self):
        logging.info('Updater thread started')
        init_jobs()

        while True:
            schedule.run_pending()
            time.sleep(1)
