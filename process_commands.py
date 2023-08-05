import content_generator
import db_access
from objects.astronauts_data import AstronautsData


def process_welcome(message):
    db_access.store_query(message.text, message.from_user, message.chat.id)
    db_access.store_user(message.from_user, message.chat.id)


def process_people_in_orbit(message):
    text, astronauts_data = content_generator.get_people_in_orbit()
    db_access.store_query(message.text, message.from_user, message.chat.id, {'astronauts_count': len(astronauts_data)})
    db_access.store_user(message.from_user, message.chat.id)

    payload = AstronautsData(astronauts_data, len(astronauts_data) > 0)
    db_access.store_interval_data(payload)
    if not db_access.get_valid_daily_data():
        db_access.store_daily_data(payload)
    return text
