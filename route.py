from bs4 import BeautifulSoup
import requests
import random
import logging

class FindRandomRoute:
    def __init__(self):
        self.starting_url = None
        self.route_link = None
        self.gps_value = None

    def get_area(self, url):
        self.starting_url = url
        area_links = []
        area_weights = []
        page = BeautifulSoup(requests.get(url).text, 'html.parser')
        areas_section = page.find_all('div', class_="lef-nav-row")
        if len(areas_section) > 0:
            for area in areas_section:
                area_links.append(area.find('a')['href'])
                area_weights.append(int(area.find("span", class_="text-warm").get_text(strip=True).replace(",", "")))
            picked_area = random.choices(area_links, area_weights, k=1)[0]
            return self.get_area(picked_area)
        else:
            logging.debug('End of areas cycle (len(areas_section) == 0)')
            return self.get_route(url)

    def get_route(self, url):
        get_route = BeautifulSoup(requests.get(url).text, 'html.parser')
        table = get_route.find('table', id='left-nav-route-table')
        hrefs = []
        if table:
            for tr in table.find_all('tr'):
                for a in tr.find_all('a', href=True):
                    hrefs.append(a['href'])
            picked_route = random.choice(hrefs)
            self.route_link = picked_route
            return self.get_image(picked_route)
        else:
            print('No routes found')
            logging.debug('No routes')

    def get_image(self, url):
        get_images = BeautifulSoup(requests.get(url).text, 'html.parser').find_all('div', class_='col-xs-4')
        img_list = []
        for img in get_images:
            img_list.append(img.find('a')['href'])
        gps_label = BeautifulSoup(requests.get(url).text, 'html.parser').find("td", string="GPS:")
        self.gps_value = gps_label.find_next_sibling("td").get_text(strip=True)
        if len(img_list) > 0:
            picked_img = random.choice(img_list)
            final_image = BeautifulSoup(requests.get(picked_img).text, 'html.parser').find('img', class_='img-fluid main-photo')[
                'src']
            return final_image, self.route_link, self.gps_value
        else:
            return self.get_area(self.starting_url)



if __name__ == '__main__':
    print('\n*** Route GuessR ***')
    area = input("\nEnter a MP Area Link: ")
    route_guess = FindRandomRoute().get_area(area)
    print(route_guess)
    #app.run(debug=True, host='0.0.0.0', port=5000)