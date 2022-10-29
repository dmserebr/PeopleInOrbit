import logging
import threading
import time

import schedule

import config
import db_access
import http_data_loader
import wiki_parser


def update_astronaut_data():
    logging.info('Updating astronaut data according to schedule')
    astronauts_data = None
    try:
        page_soup = http_data_loader.load_astronauts()
        astronauts_data = wiki_parser.get_astronauts(page_soup)
    except Exception:
        logging.exception('Error while updating astronauts data')

    db_access.store_data({'astronauts': astronauts_data})


def init_jobs():
    schedule.every().day.at(config.UPDATER_START_TIME).do(update_astronaut_data).tag('update_astronaut_data')


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
