# Config data for bot
import os

BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_ENABLED = True

# Http loader settings
WIKI_URL = 'https://en.wikipedia.org'
PEOPLE_IN_ORBIT_URL = WIKI_URL + '/wiki/Low_Earth_orbit'

# Database settings
DB_FILENAME = 'database.db'

# Updater settings
UPDATER_ENABLED = True
UPDATER_START_TIME = '11:00'
UPDATER_SEND_MESSAGES_ENABLED = True

# Flask app settings
FLASK_APP_ENABLED = True
FLASK_APP_PORT = 5742
FLASK_APP_DEBUG = False

FIREBASE_NOTIFICATIONS_ENABLED = True
FIREBASE_KEY_PATH = os.environ['FIREBASE_KEY_PATH'] if FIREBASE_NOTIFICATIONS_ENABLED else None

