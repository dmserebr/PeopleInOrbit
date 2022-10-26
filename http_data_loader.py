import requests
from bs4 import BeautifulSoup

import config


def load_astronauts():
    people_in_orbit_page = requests.get(config.PEOPLE_IN_ORBIT_URL)
    soup = BeautifulSoup(people_in_orbit_page.content, 'html.parser')
    return soup
