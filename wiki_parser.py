def get_astronauts(soup):
    def box_search_condition(txt):
        return txt and txt.startswith("People_currently_in_low_Earth_orbit")

    table_root = soup.find(id=box_search_condition).parent.parent.parent
    station_rows = table_root.find_all('tr', recursive=False)

    astronauts = []
    for station_row in station_rows:
        header_col = station_row.find('th', class_='navbox-group')
        if header_col:
            station_a = header_col.find('a')
            station_name = station_a.get_text()
            station_url = station_a['href']

            mission_rows_table = station_row.find('td').find('table')
            if mission_rows_table:
                mission_rows = mission_rows_table.find('tbody')
                for mission_row in mission_rows:
                    mission_header = mission_row.find('th')
                    mission_name = mission_header.get_text()
                    mission_url = None
                    mission_a = mission_header.find('a')
                    if mission_a:
                        mission_name = mission_a.get_text()
                        mission_url = mission_a['href']

                    astronaut_rows = mission_row.find('td').find('div').find('ul').find_all('li')
                    process_astronaut_rows(astronauts, astronaut_rows,
                                           mission_name, mission_url, station_name, station_url)
            else:
                # hack for Polaris Dawn (0924)
                no_mission_rows = station_row.find('td').find('div')
                astronaut_rows = no_mission_rows.find('ul').find_all('li')
                process_astronaut_rows(astronauts, astronaut_rows,
                                       station_name, station_url, station_name, station_url)

    return astronauts


def process_astronaut_rows(astronauts, astronaut_rows, mission_name, mission_url, station_name, station_url):
    for astronaut_row in astronaut_rows:
        astronaut_a = astronaut_row.find('a', recursive=False)
        astronaut_name = astronaut_a.get_text()
        astronaut_url = astronaut_a['href']
        country_with_url = astronaut_row.find('span', class_='flagicon').find('a')
        if country_with_url:  # before 06-23
            country_name = country_with_url['title']
            country_url = country_with_url['href']
        else:
            country_name = astronaut_row.contents[1].text[:-1]
            country_url = None

        astronauts.append({
            'name': astronaut_name,
            'url': astronaut_url,
            'country': country_name,
            'country_url': country_url,
            'mission_name': mission_name,
            'mission_url': mission_url,
            'station_name': station_name,
            'station_url': station_url
        })


def get_person_image(soup):
    image_row = soup.find('td', class_='infobox-image')
    if image_row:
        return {
            'src': image_row.find('img')["src"],
            'width': int(image_row.find('img')['width']),
            'height': int(image_row.find('img')['height'])
        }
    return None
