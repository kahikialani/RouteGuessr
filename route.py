from bs4 import BeautifulSoup
import requests
import random
import logging

class FindRandomRoute:
    def __init__(self):
        self.call_count = 0
        self.data = {
            'image_url': None,
            'route_url': None,
            'starting_url': None,
            'route_name': None,
            'area_name': None,
            'area_lat': None,
            'area_lon': None,
            'route_lat': None,
            'route_lon': None,
        }

    def get_area(self, url):
        self.call_count += 1
        if self.call_count > 10:
            logging.error('Too many calls to get area')
            return None
        self.data['starting_url'] = url
        area_links = []
        area_weights = []
        page = BeautifulSoup(requests.get(url).text, 'html.parser')
        areas_section = page.find_all('div', class_="lef-nav-row")
        if self.call_count == 1:
            area_gps_label = page.find("td", string="GPS:")
            area_gps = area_gps_label.find_next_sibling("td").get_text(strip = True).split('Google')[0].strip()

            gps_lat, gps_lon = area_gps.split(',')
            self.data['area_lat'] = float(gps_lat)
            self.data['area_lon'] = float(gps_lon)

            area_name = page.find('h1').get_text(strip = True)[:-8]
            self.data['area_name'] = area_name

        if len(areas_section) > 0:
            for sub_area in areas_section:
                area_links.append(sub_area.find('a')['href'])
                area_weights.append(int(sub_area.find("span", class_="text-warm").get_text(strip=True).replace(",", "")))

            picked_area = random.choices(area_links, area_weights, k=1)[0]
            logging.debug('picked area: %s', picked_area)

            return self.get_area(picked_area)

        else:
            logging.debug('End of areas cycle, getting routes')
            return self.get_route(url)

    def get_route(self, url):
        logging.debug(f'get_route(): {url}')
        get_route = BeautifulSoup(requests.get(url).text, 'html.parser')
        table = get_route.find('table', id='left-nav-route-table')
        hrefs = []

        if table:
            for tr in table.find_all('tr'):
                for a in tr.find_all('a', href=True):
                    hrefs.append(a['href'])

            logging.debug(f"found {len(hrefs)} routes")
            picked_route = random.choice(hrefs)
            self.data['route_url'] = picked_route
            logging.debug(f'picked: {picked_route}')

            return self.get_image(picked_route)

        else:
            print('No routes found')
            logging.debug('No routes')
            return None

    def get_image(self, url):
        logging.debug(f"get_image(): {url}")
        route_page = BeautifulSoup(requests.get(url).text, 'html.parser')

        route_name = route_page.find('h1').get_text(strip = True)
        self.data['route_name'] = route_name

        get_images = route_page.find_all('div', class_='col-xs-4')
        img_list = []

        for img in get_images:
            img_list.append(img.find('a')['href'])
        logging.debug(f"found {len(img_list)} images")

        gps_label = BeautifulSoup(requests.get(url).text, 'html.parser').find("td", string="GPS:")
        gps_value = gps_label.find_next_sibling("td").get_text(strip=True)
        gps_lat, gps_lon = gps_value.split(',')
        self.data['route_lat'] = float(gps_lat)
        self.data['route_lon'] = float(gps_lon)

        if len(img_list) > 0:
            picked_img = random.choice(img_list)
            final_image = BeautifulSoup(requests.get(picked_img).text, 'html.parser').find('img', class_='img-fluid main-photo')['src']
            self.data['image_url'] = final_image
            return self.data
        else:
            return self.get_area(self.data['starting_url'])



if __name__ == '__main__':
    print('\n*** Route GuessR ***')
    area = input("\nEnter a MP Area Link: ")
    route_guess = FindRandomRoute().get_area(area)
    print(route_guess)