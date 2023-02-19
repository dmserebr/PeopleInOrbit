import logging
import threading

from flask import Flask, request

import config
import db_access
import message_formatter

app = Flask(__name__)


@app.route('/data/astronauts', methods=['GET'])
def index():
    logging.debug(f'Handling {request.method} {request.path}')

    result = {}
    try:
        last_daily_data = db_access.get_daily_data()
        astronauts = last_daily_data['astronauts']

        items = []
        for astronaut in astronauts:
            item = {
                'name': astronaut['name'],
                'wiki_url': config.WIKI_URL + astronaut['url'],
                'country': astronaut['country'],
                'flag': message_formatter.get_country_emoji(astronaut['country']),
                'station': astronaut['station_name']
            }
            if astronaut['image']:
                item['image'] = astronaut['image']
                items.append(item)

        return {'items': items}
    except Exception:
        logging.exception('Error while getting astronauts')

    return result


class FlaskAppThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'FlaskAppThread'
        self.daemon = True

    def run(self):
        logging.info('Flask app thread started')
        app.run(threaded=True, debug=config.FLASK_APP_DEBUG, port=config.FLASK_APP_PORT)
