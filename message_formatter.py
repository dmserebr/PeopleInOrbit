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
    'Italy': '🇮🇹',
    'United Arab Emirates': '🇦🇪',
    'UAE': '🇦🇪',
    'Saudi Arabia': '🇸🇦',
    'Denmark': '🇩🇰',
    'Turkey': '🇹🇷',
    'Türkiye': '🇹🇷',
    'Sweden': '🇸🇪',
    'Belarus': '🇧🇾'
}

MISSING_COUNTRY = '🇺🇳'


def get_country_emoji(country_name):
    emoji = COUNTRY_EMOJIS.get(country_name)
    if not emoji:
        logging.warning(f'Missing emoji for country {country_name}')
        return MISSING_COUNTRY
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

    return '\n\n'.join(msgs) + '\n\nVisit our webpage at https://peopleinspacenow.com or go to /peopleinorbit ' \
                               'to see all people in orbit right now 🧑‍🚀'


def format_added_firebase(astronauts):
    title = f'🎉🎉 {len(astronauts)} new people in orbit'
    descriptions = []
    for station_name, astronauts_at_station in itertools.groupby(astronauts, key=lambda x: x['station_name']):
        astronaut_titles = []
        for astronaut in astronauts_at_station:
            astronaut_titles.append(astronaut['name'] + ' ' + get_country_emoji(astronaut['country']))
        msg = ', '.join(astronaut_titles) + ' have joined ' + station_name
        descriptions.append(msg)
    return {'title': title, 'description': '\n\n'.join(descriptions)}


def format_removed(astronauts):
    msgs = []
    for station_name, astronauts_at_station in itertools.groupby(astronauts, key=lambda x: x['station_name']):
        astronauts_at_station = list(astronauts_at_station)
        msg = f'<b>😢😢\n\n{len(astronauts_at_station)} people have just left {station_name}...</b>'

        for astronaut in astronauts_at_station:
            msg += '\n • ' + astronaut['name'] + ' ' + get_country_emoji(astronaut['country'])
        msgs.append(msg)

    return '\n\n'.join(msgs) + '\n\nVisit our webpage at https://peopleinspacenow.com or go to /peopleinorbit ' \
                               'to see all people in orbit right now 🧑‍🚀'


def format_removed_firebase(astronauts):
    title = f'😢😢 {len(astronauts)} people left orbit'
    descriptions = []
    for station_name, astronauts_at_station in itertools.groupby(astronauts, key=lambda x: x['station_name']):
        astronaut_titles = []
        for astronaut in astronauts_at_station:
            astronaut_titles.append(astronaut['name'] + ' ' + get_country_emoji(astronaut['country']))
        msg = ', '.join(astronaut_titles) + ' have left ' + station_name
        descriptions.append(msg)
    return {'title': title, 'description': '\n\n'.join(descriptions)}
