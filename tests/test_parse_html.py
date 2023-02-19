import json
from pathlib import Path

import http_data_loader
import wiki_parser

CURRENT_DIR = Path(__file__).parent


def load_resource(resource_name):
    return open(CURRENT_DIR / 'resources' / resource_name, encoding='utf-8').read()


def test_parse_html(mocker):
    mocker.patch.object(http_data_loader, 'load_page_content', return_value=load_resource('test_page_body'))

    page_soup = http_data_loader.load_astronauts()
    astronauts_data = wiki_parser.get_astronauts(page_soup)

    expected_data = json.loads(load_resource('test_astronauts_data.json'))
    assert expected_data == astronauts_data


def test_parse_person_page(mocker):
    # data taken from url='https://en.wikipedia.org/wiki/Sergey_Prokopyev_(cosmonaut)'
    mocker.patch.object(http_data_loader, 'load_page_content', return_value=load_resource('test_page_body_person'))

    page_soup = http_data_loader.load_from_url('')
    data = wiki_parser.get_person_image(page_soup)

    expected_data = {
        'src': '//upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Sergey_Prokopyev_-_NASA_portrait.jpg/'
               '200px-Sergey_Prokopyev_-_NASA_portrait.jpg',
        'alt': 'Sergey Prokopyev - NASA portrait.jpg',
        'width': 200,
        'height': 258
    }
    assert expected_data == data
