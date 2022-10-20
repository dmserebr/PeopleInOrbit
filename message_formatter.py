import itertools

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
        print(f'Missing emoji for country {country_name}')
    return emoji


def generate_msg(astronauts):
    msg = f'<b>There are currently {len(astronauts)} people in low Earth orbit.</b>'

    for station_name, astronauts_at_station in itertools.groupby(astronauts, key=lambda x: x['station_name']):
        print(station_name)
        astronauts_at_station = list(astronauts_at_station)
        msg += f'\n\n<b>{station_name}:</b> {len(astronauts_at_station)} people'

        for astronaut in astronauts_at_station:
            msg += '\n • ' + astronaut['name'] + ' ' + get_country_emoji(astronaut['country'])

    return msg
