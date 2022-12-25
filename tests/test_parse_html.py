import json
from pathlib import Path

CURRENT_DIR = Path(__file__).parent


def load_resource(resource_name):
    return open(CURRENT_DIR / 'resources' / resource_name, encoding='utf-8').read()


def test_parse_html(mocker):
    import http_data_loader, wiki_parser

    mocker.patch.object(http_data_loader, 'load_page_content', return_value=load_resource('test_page_body'))

    page_soup = http_data_loader.load_astronauts()
    astronauts_data = wiki_parser.get_astronauts(page_soup)

    expected_data = json.loads(load_resource('test_astronauts_data.json'))
    assert expected_data == astronauts_data
