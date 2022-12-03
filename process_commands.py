import content_generator
import db_access


def process_welcome(message):
    db_access.store_query(message.text, message.from_user, message.chat.id)
    db_access.store_user(message.from_user, message.chat.id)


def process_people_in_orbit(message):
    text, astronauts_data = content_generator.get_people_in_orbit()
    db_access.store_query(message.text, message.from_user, message.chat.id, {'astronauts_count': len(astronauts_data)})
    db_access.store_user(message.from_user, message.chat.id)
    db_access.store_data({'astronauts': astronauts_data})
    return text
