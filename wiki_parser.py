def get_astronauts(soup):
    table_root = soup.find(id="People_currently_in_low_Earth_orbit").parent.parent.parent
    station_rows = table_root.find_all('tr', recursive=False)

    astronauts = []
    for station_row in station_rows:
        header_col = station_row.find('th', {'class': 'navbox-group'})
        if header_col:
            station_a = header_col.find('a')
            station_name = station_a.get_text()
            station_url = station_a['href']

            mission_rows = station_row.find('td').find('table').find('tbody')
            for mission_row in mission_rows:
                mission_a = mission_row.find('th').find('a')
                mission_name = mission_a.get_text()
                mission_url = mission_a['href']

                astronaut_rows = mission_row.find('td').find('div').find('ul').find_all('li')
                for astronaut_row in astronaut_rows:
                    astronaut_a = astronaut_row.find('a', recursive=False)
                    astronaut_name = astronaut_a.get_text()
                    astronaut_url = astronaut_a['href']
                    country = astronaut_row.find('span', {'class': 'flagicon'}).find('a')
                    country_name = country['title']
                    country_url = country['href']

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
    return astronauts
