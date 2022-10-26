import http_data_loader
import message_formatter
import wiki_parser


def get_people_in_orbit():
    text = 'Cannot get information about people in orbit 😕\nPlease contact the bot administrator.'
    astronauts_data = None

    try:
        page_soup = http_data_loader.load_astronauts()
        astronauts_data = wiki_parser.get_astronauts(page_soup)
        text = message_formatter.generate_msg(astronauts_data)
    except Exception as e:
        print('Got exception: ', e.__repr__(), e.args)

    return text, astronauts_data
