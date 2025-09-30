from unittest.mock import create_autospec

from bs4 import BeautifulSoup
import requests
import logging
import time
import re
import psycopg2
import os
import sqlite3
from dotenv import load_dotenv

class DataConstructor:
    def __init__(self, use_local = True, local_db_path = 'RouteGuessrDB.db', db_connection_string = '', url = 'https://www.mountainproject.com/area/105720495/joshua-tree-national-park'):
        self.session = requests.Session()
        self.area_data = {
            'area_name': str(),
            'area_lat': float(),
            'area_lon': float(),
            'total_routes': float(),
            'area_link': str()
        }
        self.input_url = url
        self.use_local = use_local
        self.current_area_id = None
        # Connection string like 'conn_str = f"dbname={PROJECT} user={USERNAME} password={PASSWORD} host={HOST} port={PORT} sslmode=require&channel_binding=require"'
        self.db_connection_string = db_connection_string
        if use_local:
            self.conn = sqlite3.connect(local_db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")
            logging.info("Local database created")
        else:
            if db_connection_string:
                try:
                    self.conn = psycopg2.connect(self.db_connection_string)
                    self.conn.autocommit = True
                    logging.info("Connected to PostgreSQL via Neon")
                except psycopg2.Error as e:
                    logging.error("Error while connecting to PostgreSQL", e)
                    self.conn = None
                    return

        self.create_tables()
        logging.info("Tables created successfully")

        self.get_main_area_info(self.input_url)
        self.get_sub_area(self.input_url)

    def close_connection(self):
        if self.conn:
            self.conn.close()
            logging.info("Connection to PostgreSQL closed")

    def __del__(self):
        self.close_connection()

    def create_tables(self):
        if self.use_local:
            # SQLite
            create_areas_table = """
            CREATE TABLE IF NOT EXISTS climbing_areas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_name TEXT NOT NULL UNIQUE,
                area_link TEXT NOT NULL UNIQUE,
                area_lat REAL NOT NULL,
                area_lon REAL NOT NULL,
                total_routes INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            );
            """

            create_routes_table = """
            CREATE TABLE IF NOT EXISTS climbing_routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_name TEXT NOT NULL,
                route_link TEXT NOT NULL UNIQUE,
                route_lat REAL NOT NULL,
                route_lon REAL NOT NULL,
                route_type TEXT NOT NULL,
                route_grade TEXT NOT NULL,
                route_stars REAL NOT NULL,
                route_length REAL NOT NULL,
                area_id INTEGER REFERENCES climbing_areas(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            );  
            """

            create_images_table = """
            CREATE TABLE IF NOT EXISTS route_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id INTEGER REFERENCES climbing_routes(id) ON DELETE CASCADE,
                image_link TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                UNIQUE (route_id, image_link)
            );
            """

            create_indexes = [
                "CREATE INDEX IF NOT EXISTS idx_route_area_id ON climbing_routes(area_id);",
                "CREATE INDEX IF NOT EXISTS idx_route_name ON climbing_routes(route_name);",
                "CREATE INDEX IF NOT EXISTS idx_images_route_id ON route_images(route_id);"
            ]
        else:
            # PostgreSQL
            create_areas_table = """
            CREATE TABLE IF NOT EXISTS climbing_areas (
                id SERIAL PRIMARY KEY,
                area_name VARCHAR(255) NOT NULL UNIQUE,
                area_link TEXT NOT NULL UNIQUE,
                area_lat FLOAT NOT NULL,
                area_lon FLOAT NOT NULL,
                total_routes INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            );
            """

            create_routes_table = """
            CREATE TABLE IF NOT EXISTS climbing_routes (
                id SERIAL PRIMARY KEY,
                route_name VARCHAR(255) NOT NULL, 
                route_link TEXT NOT NULL UNIQUE,
                route_lat FLOAT NOT NULL,
                route_lon FLOAT NOT NULL,
                route_type VARCHAR(255) NOT NULL,
                route_grade VARCHAR(255) NOT NULL,
                route_stars FLOAT NOT NULL,
                route_length FLOAT NOT NULL,
                area_id INTEGER REFERENCES climbing_areas(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            );
            """

            create_images_table = """
            CREATE TABLE IF NOT EXISTS route_images (
                id SERIAL PRIMARY KEY,
                route_id INTEGER REFERENCES climbing_routes(id) ON DELETE CASCADE,
                image_link TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (route_id, image_link)
            );
            """

            create_indexes = """
            CREATE INDEX IF NOT EXISTS idx_routes_area_id ON climbing_routes(area_id);
            CREATE INDEX IF NOT EXISTS idx_routes_name ON climbing_routes(route_name);
            CREATE INDEX IF NOT EXISTS idx_images_route_id ON route_images(route_id);
            """
        try:
            if self.use_local:
                cur = self.conn.cursor()
                cur.execute(create_areas_table)
                cur.execute(create_routes_table)
                cur.execute(create_images_table)
                for index_sql in create_indexes:
                    cur.execute(index_sql)
                self.conn.commit()
                logging.info('SQLite tables created successfully')
            else:
                with self.conn.cursor() as cur:
                    cur.execute(create_areas_table)
                    cur.execute(create_routes_table)
                    cur.execute(create_images_table)
                    cur.execute(create_indexes)
                logging.info('PostgreSQL tables created successfully')
            logging.info('All tables have been successfully created and pushed to Neon')
        except psycopg2.Error as e:
            logging.error(f"Error creating tables: {e}")

    def save_area_data(self):
        if self.use_local:
            try:
                # SQLite (Local)
                insert_query = """
                INSERT OR REPLACE INTO climbing_areas(area_name, area_link, area_lat, area_lon, total_routes)
                VALUES (?, ?, ?, ?, ?)
                """
                cur = self.conn.cursor()
                cur.execute(insert_query, (
                    self.area_data['area_name'],
                    self.area_data['area_link'],
                    self.area_data['area_lat'],
                    self.area_data['area_lon'],
                    self.area_data['total_routes']
                ))
                self.conn.commit()
                area_id = cur.lastrowid
                self.current_area_id = area_id
                logging.info(f'Area saved: {self.area_data["area_name"]} (ID: {area_id})')
                return area_id
            except Exception as e:
                logging.error(f'Error saving main area: {e}')
        else:
            # PostgreSQL
            insert_query = """
            INSERT INTO climbing_areas (area_name, area_link, area_lat, area_lon, total_routes)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (area_name) DO UPDATE SET
                area_lat = EXCLUDED.area_lat,
                area_lon = EXCLUDED.area_lon,
                total_routes = EXCLUDED.total_routes
            RETURNING id;
            """
            try:
                with self.conn.cursor() as cur:
                    cur.execute(insert_query, (
                        self.area_data['area_name'],
                        self.area_data['area_link'],
                        self.area_data['area_lat'],
                        self.area_data['area_lon'],
                        self.area_data['total_routes']
                    ))
                    area_id = cur.fetchone()[0]
                self.current_area_id = area_id
                logging.info(f'Area saved: {self.area_data["area_name"]} (ID: {area_id})')
                return area_id
            except psycopg2.Error as e:
                logging.error(f"Error saving area data: {e}")
                return None

    def save_route_data(self, route_data):
        if self.use_local:
            try:
                insert_query = """
                INSERT OR REPLACE INTO climbing_routes
                (route_name, route_link, route_lat, route_lon, route_type, route_grade, route_stars, route_length, area_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cur = self.conn.cursor()
                cur.execute(insert_query, (
                    route_data['route_name'],
                    route_data['route_link'],
                    route_data['route_lat'],
                    route_data['route_lon'],
                    route_data['route_type'],
                    route_data['route_grade'],
                    route_data['route_stars'],
                    route_data['route_length'],
                    self.current_area_id
                ))
                self.conn.commit()
                route_id = cur.lastrowid
                logging.info(f'Routes saved: {route_data["route_name"]} (ID: {route_id})')
                return route_id
            except Exception as e:
                logging.error(f'Error saving {route_data["route_name"]}: {e}')
                return None
        else:
            # PostgreSQL (Hosted DB)
            insert_query = """
            INSERT INTO climbing_routes
            (route_name, route_link, route_lat, route_lon, route_type, route_length, route_grade, route_stars, area_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (route_link) DO UPDATE SET
                route_lat = EXCLUDED.route_lat,
                route_lon = EXCLUDED.route_lon,
                route_type = EXCLUDED.route_type,
                route_length = EXCLUDED.route_length,
                route_grade = EXCLUDED.route_grade,
                route_stars = EXCLUDED.route_stars
            RETURNING id;
            """

            try:
                with self.conn.cursor() as cur:
                    cur.execute(insert_query, (
                        route_data['route_name'],
                        route_data['route_link'],
                        route_data['route_lat'],
                        route_data['route_lon'],
                        route_data['route_type'],
                        route_data['route_length'],
                        route_data['route_grade'],
                        route_data['route_stars'],
                        self.current_area_id
                    ))
                    route_id = cur.fetchone()[0]
                    logging.info(f'Routes saved: {route_data["route_name"]} (ID: {route_id})')
                    return route_id
            except psycopg2.Error as e:
                logging.error(f"Error saving route data: {e}")
                return None

    def save_route_images(self, route_id, image_links):
        if route_id is None:
            logging.warning("Cannot save images: route_id is None")
            return

        if self.use_local:
            try:
                insert_query = """
                INSERT OR IGNORE INTO route_images
                (route_id, image_link)
                VALUES (?, ?)
                """
                cur = self.conn.cursor()
                image_data = [(route_id, img_link) for img_link in image_links]
                cur.executemany(insert_query, image_data)
                self.conn.commit()
                logging.info(f"Saved {len(image_data)} images for route ID {route_id}")
            except Exception as e:
                logging.error(f'Error saving images for route {route_id}: {e}')
        else:
            insert_query = """
            INSERT INTO route_images (route_id, image_link)
            VALUES (%s, %s)
            ON CONFLICT (route_id, image_link) DO NOTHING;
            """

            try:
                with self.conn.cursor() as cur:
                    image_data = [(route_id, img_link) for img_link in image_links]
                    cur.executemany(insert_query, image_data)
                    logging.info(f"Saved {len(image_data)} images for route ID {route_id}")
            except psycopg2.Error as e:
                logging.error(f"Error saving image data: {e}")

    def scrape_mp(self, url):
        pass

    def get_main_area_info(self, url):
        logging.info(f"Getting main area info for {url}")
        try:
            page = BeautifulSoup(self.session.get(url).text, 'html.parser')

            area_name = page.find('h1').get_text(strip=True)[:-8]
            self.area_data['area_name'] = area_name
            self.area_data['area_link'] = url

            area_gps_label = page.find("td", string="GPS:")
            area_gps = area_gps_label.find_next_sibling("td").get_text(strip=True).split('Google')[0].strip()

            gps_lat, gps_lon = area_gps.split(',')
            self.area_data['area_lat'] = float(gps_lat)
            self.area_data['area_lon'] = float(gps_lon)

            areas_section = page.find_all('div', class_="lef-nav-row")

            area_climb_counts = []
            if len(areas_section) > 0:
                for sub_area in areas_section:
                    area_climb_counts.append(
                        int(sub_area.find("span", class_="text-warm").get_text(strip=True).replace(",", "")))
            self.area_data['total_routes'] = sum(area_climb_counts)
            logging.info(f"Main area data received, sending data to save_area_data()")
            self.save_area_data()
        except Exception as e:
            logging.error(f"Exception: {e}")

    def get_sub_area(self, url):
        logging.info(f"Getting sub area info for {url}")
        logging.info(f'waiting for time.sleep')
        time.sleep(4)
        try:
            page = BeautifulSoup(self.session.get(url).text, 'html.parser')
            areas_section = page.find_all('div', class_="lef-nav-row")
            if len(areas_section) > 0:
                for sub_area in areas_section:
                    sub_area_link = sub_area.find('a')['href']
                    logging.debug(f'found sub_area at {sub_area_link}')
                    self.get_sub_area(sub_area_link)
            else:
                logging.debug(f'found no sub areas')
                logging.debug(f'The leaf of the sub areas is {url}')
                self.get_route_page(url)
        except Exception as e:
            logging.error(f"Exception: {e}")

    def get_route_page(self, url):
        logging.debug(f"getting routes from last sub area: {url}")
        logging.info(f'waiting for time.sleep')
        time.sleep(4)
        try:
            page = BeautifulSoup(self.session.get(url).text, 'html.parser')
            table = page.find('table', id='left-nav-route-table')
            hrefs = []

            if table:
                for tr in table.find_all('tr'):
                    for a in tr.find_all('a', href=True):
                        hrefs.append(a['href'])
            else:
                logging.debug(f'no routes found')
                return

            for link in hrefs:
                self.get_route_data(link)
        except Exception as e:
            logging.error(f"Exception: {e}")

    def get_route_data(self, url):
        route_data = {}
        logging.debug(f"getting ROUTE data: {url}")
        logging.info(f'waiting for time.sleep')
        time.sleep(4)
        try:
            page = BeautifulSoup(self.session.get(url).text, 'html.parser')
            # Checks if there are images.
            # If there aren't images, there is no point adding the route to the database.
            html_images = page.find_all('div', class_='col-xs-4')
            img_list = []
            for img in html_images:
                img_link = img.find('a')['href']
                img_list.append(img_link)

            if len(img_list) > 0:
                # Basic Data
                route_name = page.find('h1').get_text(strip = True)
                route_data['route_name'] = route_name
                route_data['route_link'] = url
                route_data['route_grade'] = page.find('span', class_='rateYDS').text.split()[0]

                # Find stars
                stars_span = page.find('span', id=re.compile(r'starsWithAvgText-\d+')).text
                stars = re.search(r'Avg:\s*([\d\.]+)', stars_span).group(1)
                route_data['route_stars'] = float(stars)

                # Find type
                type_label = page.find("td", string="Type:")
                route_type = type_label.find_next_sibling("td").get_text(strip=True).split(',')[0]
                route_data['route_type'] = route_type

                # Find length
                length_label = page.find("td", string="Type:")
                length_string = length_label.find_next_sibling("td").get_text(strip=True).split(',')[1]
                route_length = float(length_string.split(' ')[1])
                route_data['route_length'] = route_length

                # Find GPS coordinates
                gps_label = page.find("td", string="GPS:")
                gps_value = gps_label.find_next_sibling("td").get_text(strip=True)
                gps_lat, gps_lon = gps_value.split(',')
                route_data['route_lat'] = float(gps_lat)
                route_data['route_lon'] = float(gps_lon)

                # Send to DB
                # save_route_data also returns route_id
                r_id = self.save_route_data(route_data)
                self.save_route_images(r_id, img_list)
        except Exception as e:
            logging.error(f"Exception: {e}")



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()
    neon_connection = os.getenv("NEON_KEY")
    if not neon_connection:
        logging.error("NEON_KEY environment variable not found")
        exit(1)
    location_url = input('Input MP link:')
    local = input("Enter 'True' or 'False': ").lower()
    if local == 'true':
        DataConstructor(use_local=True, db_connection_string=neon_connection, url=location_url)
    elif local == 'false':
        DataConstructor(use_local=False, db_connection_string=neon_connection, url=location_url)
    else:
        print("Invalid input. Please enter 'True' or 'False'.")
        boolean_local = None
