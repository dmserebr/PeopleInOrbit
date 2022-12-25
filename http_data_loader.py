import requests
from bs4 import BeautifulSoup

import config


def load_astronauts():
    people_in_orbit_page = load_page_content(config.PEOPLE_IN_ORBIT_URL)
    soup = BeautifulSoup(people_in_orbit_page, 'html.parser')
    return soup


def load_page_content(url):
    return requests.get(url).content
