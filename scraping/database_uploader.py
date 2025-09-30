import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
import logging
from dotenv import load_dotenv
import os


class DatabaseMigrator:
    def __init__(self, sqlite_path='RouteGuessrDB.db', postgres_connection_string=''):
        self.sqlite_path = sqlite_path
        self.postgres_connection_string = postgres_connection_string
        self.sqlite_conn = None
        self.postgres_conn = None

    def connect_databases(self):
        try:
            # SQLite
            self.sqlite_conn = sqlite3.connect(self.sqlite_path)
            self.sqlite_conn.row_factory = sqlite3.Row
            logging.info(f"Connected to SQLite database: {self.sqlite_path}")

            # PostgreSQL
            self.postgres_conn = psycopg2.connect(self.postgres_connection_string)
            self.postgres_conn.autocommit = False
            logging.info("Connected to PostgreSQL database")

            return True
        except sqlite3.Error as e:
            logging.error(f"SQLite connection error: {e}")
            return False
        except psycopg2.Error as e:
            logging.error(f"PostgreSQL connection error: {e}")
            return False

    def create_postgres_tables(self):

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
            with self.postgres_conn.cursor() as cur:
                cur.execute(create_areas_table)
                cur.execute(create_routes_table)
                cur.execute(create_images_table)
                cur.execute(create_indexes)
            self.postgres_conn.commit()
            logging.info("PostgreSQL tables created successfully")
            return True
        except psycopg2.Error as e:
            logging.error(f"Error creating PostgreSQL tables: {e}")
            self.postgres_conn.rollback()
            return False

    def migrate_climbing_areas(self):
        try:
            sqlite_cur = self.sqlite_conn.cursor()
            sqlite_cur.execute("SELECT * FROM climbing_areas ORDER BY id")
            areas = sqlite_cur.fetchall()

            if not areas:
                logging.info("No areas to migrate")
                return {}

            logging.info(f"Found {len(areas)} areas to migrate")

            insert_query = """
            INSERT INTO climbing_areas (area_name, area_link, area_lat, area_lon, total_routes, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (area_name) DO UPDATE SET
                area_link = EXCLUDED.area_link,
                area_lat = EXCLUDED.area_lat,
                area_lon = EXCLUDED.area_lon,
                total_routes = EXCLUDED.total_routes;
            """

            batch_data = [
                (
                    area['area_name'],
                    area['area_link'],
                    area['area_lat'],
                    area['area_lon'],
                    area['total_routes'],
                    area['created_at']
                )
                for area in areas
            ]

            with self.postgres_conn.cursor() as pg_cur:
                execute_batch(pg_cur, insert_query, batch_data, page_size=100)

            self.postgres_conn.commit()
            logging.info(f"Inserted {len(areas)} climbing areas")

            id_mapping = {}
            with self.postgres_conn.cursor() as pg_cur:
                pg_cur.execute("SELECT id, area_name FROM climbing_areas")
                pg_areas = pg_cur.fetchall()
                name_to_new_id = {row[1]: row[0] for row in pg_areas}

            for area in areas:
                old_id = area['id']
                area_name = area['area_name']
                new_id = name_to_new_id.get(area_name)
                if new_id:
                    id_mapping[old_id] = new_id

            logging.info(f"Created ID mapping for {len(id_mapping)} areas")
            return id_mapping

        except (sqlite3.Error, psycopg2.Error) as e:
            logging.error(f"Error migrating climbing areas: {e}")
            self.postgres_conn.rollback()
            return None

    def migrate_climbing_routes(self, area_id_mapping):
        try:
            sqlite_cur = self.sqlite_conn.cursor()
            sqlite_cur.execute("SELECT * FROM climbing_routes ORDER BY id")
            routes = sqlite_cur.fetchall()

            if not routes:
                logging.info("No routes to migrate")
                return {}

            logging.info(f"Found {len(routes)} routes to migrate")

            insert_query = """
            INSERT INTO climbing_routes 
            (route_name, route_link, route_lat, route_lon, route_type, route_grade, 
             route_stars, route_length, area_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (route_link) DO UPDATE SET
                route_name = EXCLUDED.route_name,
                route_lat = EXCLUDED.route_lat,
                route_lon = EXCLUDED.route_lon,
                route_type = EXCLUDED.route_type,
                route_grade = EXCLUDED.route_grade,
                route_stars = EXCLUDED.route_stars,
                route_length = EXCLUDED.route_length,
                area_id = EXCLUDED.area_id;
            """

            batch_data = []
            for route in routes:
                old_area_id = route['area_id']
                new_area_id = area_id_mapping.get(old_area_id)

                if new_area_id is None:
                    logging.warning(f"No mapping found for area_id {old_area_id}, skipping route {route['route_name']}")
                    continue

                batch_data.append((
                    route['route_name'],
                    route['route_link'],
                    route['route_lat'],
                    route['route_lon'],
                    route['route_type'],
                    route['route_grade'],
                    route['route_stars'],
                    route['route_length'],
                    new_area_id,
                    route['created_at']
                ))

            with self.postgres_conn.cursor() as pg_cur:
                execute_batch(pg_cur, insert_query, batch_data, page_size=100)
            self.postgres_conn.commit()
            logging.info(f"Inserted {len(batch_data)} climbing routes")

            route_id_mapping = {}
            with self.postgres_conn.cursor() as pg_cur:
                pg_cur.execute("SELECT id, route_link FROM climbing_routes")
                pg_routes = pg_cur.fetchall()
                link_to_new_id = {row[1]: row[0] for row in pg_routes}

            for route in routes:
                old_route_id = route['id']
                route_link = route['route_link']
                new_route_id = link_to_new_id.get(route_link)
                if new_route_id:
                    route_id_mapping[old_route_id] = new_route_id

            logging.info(f"Created ID mapping for {len(route_id_mapping)} routes")
            return route_id_mapping

        except (sqlite3.Error, psycopg2.Error) as e:
            logging.error(f"Error migrating climbing routes: {e}")
            self.postgres_conn.rollback()
            return None

    def migrate_route_images(self, route_id_mapping):
        try:
            sqlite_cur = self.sqlite_conn.cursor()
            sqlite_cur.execute("SELECT * FROM route_images ORDER BY id")
            images = sqlite_cur.fetchall()

            if not images:
                logging.info("No images to migrate")
                return True
            logging.info(f"Found {len(images)} images to migrate")

            insert_query = """
            INSERT INTO route_images (route_id, image_link, created_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (route_id, image_link) DO NOTHING;
            """

            batch_data = []
            skipped = 0
            for image in images:
                old_route_id = image['route_id']
                new_route_id = route_id_mapping.get(old_route_id)

                if new_route_id is None:
                    skipped += 1
                    continue

                batch_data.append((
                    new_route_id,
                    image['image_link'],
                    image['created_at']
                ))

            if skipped > 0:
                logging.warning(f"Skipped {skipped} images with no route mapping")

            with self.postgres_conn.cursor() as pg_cur:
                execute_batch(pg_cur, insert_query, batch_data, page_size=500)

            self.postgres_conn.commit()
            logging.info(f"Migrated {len(batch_data)} route images")
            return True

        except (sqlite3.Error, psycopg2.Error) as e:
            logging.error(f"Error migrating route images: {e}")
            self.postgres_conn.rollback()
            return False

    def migrate_all(self):
        logging.info("Starting database migration...")

        if not self.connect_databases():
            logging.error("Failed to connect to databases")
            return False

        if not self.create_postgres_tables():
            logging.error("Failed to create PostgreSQL tables")
            return False

        area_id_mapping = self.migrate_climbing_areas()
        if area_id_mapping is None:
            logging.error("Failed to migrate climbing areas")
            return False

        route_id_mapping = self.migrate_climbing_routes(area_id_mapping)
        if route_id_mapping is None:
            logging.error("Failed to migrate climbing routes")
            return False

        if not self.migrate_route_images(route_id_mapping):
            logging.error("Failed to migrate route images")
            return False

        logging.info("Migration completed successfully!")
        return True

    def close_connections(self):
        if self.sqlite_conn:
            self.sqlite_conn.close()
            logging.info("SQLite connection closed")
        if self.postgres_conn:
            self.postgres_conn.close()
            logging.info("PostgreSQL connection closed")

    def __del__(self):
        self.close_connections()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    load_dotenv()
    neon_connection = os.getenv("NEON_KEY")
    sqlite_path = 'RouteGuessrDB.db'

    if not neon_connection:
        logging.error("NEON_KEY environment variable not found")
        exit(1)

    print(f"\nAbout to migrate from:")
    print(f"  SQLite: {sqlite_path}")
    print(f"  To PostgreSQL (Neon)")
    confirm = input("\nProceed with migration? (y/n): ").lower()

    if confirm == 'y':
        migrator = DatabaseMigrator(
            sqlite_path=sqlite_path,
            postgres_connection_string=neon_connection
        )
        success = migrator.migrate_all()
        migrator.close_connections()
        if success:
            print("Migration completed")
        else:
            print("Migration failed")
    else:
        print("Migration cancelled")