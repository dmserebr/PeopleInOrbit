import logging
import threading
import time
from datetime import date, datetime

import schedule

import config
import db_access
import firebase_sender
import http_data_loader
import message_formatter
import send_messages
import wiki_parser
from objects.astronauts_data import AstronautsData


def process_updates():
    logging.info('Updating astronaut data according to schedule')
    astronauts_data = get_astronauts_data()

    db_access.store_interval_data(astronauts_data)
    db_access.store_daily_data(astronauts_data)

    if not astronauts_data.is_valid:
        return

    day, data_for_yesterday = db_access.get_valid_daily_data(exclude_today=True)
    parsed_day = datetime.strptime(day, "%Y-%m-%d").date()

    if (date.today() - parsed_day).days > config.UPDATER_MAX_DAYS_TO_TRY_RESTORE:
        logging.warning('Last successful update was at {parsed_day}, do not send stale updates')
        return

    astronauts_data_for_yesterday = data_for_yesterday if data_for_yesterday else AstronautsData()

    # send updates
    updates = calculate_updates(astronauts_data, astronauts_data_for_yesterday)
    if updates and config.UPDATER_SEND_MESSAGES_ENABLED:
        logging.info('Sending updates to all users')
        send_messages.send_updates_to_all_users(updates)

        if config.FIREBASE_NOTIFICATIONS_ENABLED:
            logging.info('Sending push notifications to Firebase')
            notifications = []
            if updates['added']:
                added_notifications = message_formatter.format_added_firebase(updates['added'])
                notifications.append(added_notifications)
            if updates['removed']:
                removed_notifications = message_formatter.format_removed_firebase(updates['removed'])
                notifications.append(removed_notifications)

            if notifications:
                firebase_sender.send_push_notifications(notifications)


def get_astronauts_data():
    logging.info('Start get_astronauts_data')
    result = AstronautsData()

    try:
        page_soup = http_data_loader.load_astronauts()
        astronauts_data = wiki_parser.get_astronauts(page_soup)
        enriched_astronauts_data = enrich_with_images(astronauts_data)

        result.astronauts = enriched_astronauts_data
        result.is_valid = True
    except Exception:
        logging.exception('Error while updating astronauts data')

    logging.info('Finish get_astronauts_data')
    return result


def enrich_with_images(astronauts_data):
    result = []
    for item in astronauts_data:
        enriched_item = item.copy()
        if item['url']:
            page_soup = http_data_loader.load_from_url(config.WIKI_URL + item['url'])
            image_data = wiki_parser.get_person_image(page_soup)
            if image_data:
                enriched_item['image'] = image_data
        result.append(enriched_item)
    return result


def calculate_updates(data, data_for_yesterday):
    names_today = [astronaut['name'] for astronaut in data.astronauts]
    names_yesterday = [astronaut['name'] for astronaut in data_for_yesterday.astronauts]

    added = [astronaut for astronaut in data.astronauts if not astronaut['name'] in names_yesterday]
    removed = [astronaut for astronaut in data_for_yesterday.astronauts if not astronaut['name'] in names_today]

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
