import logging

import http_data_loader
import wiki_parser


# Integration test which calls real wiki


def test_load_and_parse_page():
    soup = http_data_loader.load_astronauts()
    astronauts = wiki_parser.get_astronauts(soup)
    logging.debug(f'Got {len(astronauts)} astronauts')

    assert len(astronauts) > 0
