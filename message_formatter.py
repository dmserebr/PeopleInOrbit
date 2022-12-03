import itertools
import logging

COUNTRY_EMOJIS = {
    'Russia': '🇷🇺',
    'United States': '🇺🇸',
    'Japan': '🇯🇵',
    'China': '🇨🇳',
    'Canada': '🇨🇦',
    'Germany': '🇩🇪',
    'France': '🇫🇷',
    'Italy': '🇮🇹'
}


def get_country_emoji(country_name):
    emoji = COUNTRY_EMOJIS[country_name]
    if not emoji:
        logging.warning(f'Missing emoji for country {country_name}')
    return emoji


def generate_msg(astronauts):
    msg = f'<b>There are currently {len(astronauts)} people in low Earth orbit.</b>'

    for station_name, astronauts_at_station in itertools.groupby(astronauts, key=lambda x: x['station_name']):
        logging.debug(station_name)
        astronauts_at_station = list(astronauts_at_station)
        msg += f'\n\n<b>{station_name}:</b> {len(astronauts_at_station)} people'

        for astronaut in astronauts_at_station:
            msg += '\n • ' + astronaut['name'] + ' ' + get_country_emoji(astronaut['country'])

    return msg


def format_added(astronauts):
    msgs = []
    for station_name, astronauts_at_station in itertools.groupby(astronauts, key=lambda x: x['station_name']):
        astronauts_at_station = list(astronauts_at_station)
        msg = f'<b>Woohoo!! 🎉🎉🎉\n\n {len(astronauts_at_station)} people have just arrived at {station_name}!</b>'

        for astronaut in astronauts_at_station:
            msg += '\n • ' + astronaut['name'] + ' ' + get_country_emoji(astronaut['country'])
        msgs.append(msg)

    return '\n\n'.join(msgs) + '\n\nGo to /peopleinorbit to see all people in orbit right now 🧑‍🚀'


def format_removed(astronauts):
    msgs = []
    for station_name, astronauts_at_station in itertools.groupby(astronauts, key=lambda x: x['station_name']):
        astronauts_at_station = list(astronauts_at_station)
        msg = f'<b>😢😢\n\n{len(astronauts_at_station)} people have just left {station_name}...</b>'

        for astronaut in astronauts_at_station:
            msg += '\n • ' + astronaut['name'] + ' ' + get_country_emoji(astronaut['country'])
        msgs.append(msg)

    return '\n\n'.join(msgs) + '\n\nGo to /peopleinorbit to see all people in orbit right now 🧑‍🚀'
