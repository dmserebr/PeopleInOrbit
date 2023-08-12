import logging

import http_data_loader
import updater_thread
import wiki_parser


# Integration test which calls real wiki


def test_load_and_parse_page():
    soup = http_data_loader.load_astronauts()
    astronauts = wiki_parser.get_astronauts(soup)
    logging.debug(f'Got {len(astronauts)} astronauts')

    assert len(astronauts) > 0


def test_load_data_with_images():
    data = updater_thread.get_astronauts_data()
    assert data.is_valid is True
    assert len(data.astronauts) > 0
