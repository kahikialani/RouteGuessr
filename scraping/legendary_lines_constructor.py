import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Float, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import logging
import os

load_dotenv()
Base = declarative_base()

# Defining Existing tables (Area, Route)
class ClimbingArea(Base):
    __tablename__ = 'climbing_areas'
    id = Column(Integer, primary_key=True)
    area_name = Column(String(255), nullable=False, unique=True)
    area_link = Column(Text, nullable=False, unique=True)
    area_lat = Column(Float, nullable=False)
    area_lon = Column(Float, nullable=False)
    total_routes = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    routes = relationship('ClimbingRoute', backref='climbing_area', lazy=True)

class ClimbingRoute(Base):
    __tablename__ = 'climbing_routes'
    id = Column(Integer, primary_key=True)
    route_name = Column(String(255), nullable=False)
    route_link = Column(Text, nullable=False, unique=True)
    route_lat = Column(Float, nullable=False)
    route_lon = Column(Float, nullable=False)
    route_type = Column(String(255), nullable=False)
    route_grade = Column(String(255), nullable=False)
    route_stars = Column(Float, nullable=False)
    route_length = Column(Float, nullable=False)
    area_id = Column(Integer, ForeignKey('climbing_areas.id', ondelete='CASCADE'))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Define New Tables (mp_descriptions, mp_comments, top_area_routes, TODO gen_descriptions )

class LegendaryLines(Base):
    __tablename__ = 'legendary_lines'
    id = Column(Integer, primary_key=True)
    route_name = Column(String(255), nullable=False)
    route_type = Column(String(255))
    grade = Column(String(255))
    pitches = Column(Integer)
    length = Column(Float)
    protection = Column(String(255))
    main_area = Column(String(255))
    crag = Column(String(255))


class MpDescriptions(Base):
    __tablename__ = 'mp_descriptions'
    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('climbing_routes.id'), nullable=False)
    description = Column(Text)
    location = Column(Text)
    protection = Column(Text)

    route = relationship('ClimbingRoute')


class MpComments(Base):
    __tablename__ = 'mp_comments'
    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('climbing_routes.id'), nullable=False)
    comment_text = Column(Text)

    route = relationship('ClimbingRoute')

def init_db(key):
    engine = create_engine(key)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session

def create_authenticated_session(account, password):
    session = requests.Session()

    login_page_url = "https://www.mountainproject.com/auth/login"
    login_page = session.get(login_page_url)
    soup = BeautifulSoup(login_page.text, 'html.parser')

    csrf_token = soup.find('input', {'name': '_token'})

    if not csrf_token:
        print("Could not find CSRF token")
        return None

    token_value = csrf_token.get('value')
    logging.info(f"Found CSRF token: {token_value[:20]}...")

    login_data = {
        'email': account,
        'pass': password,
        '_token': token_value
    }

    login_url = "https://www.mountainproject.com/auth/login/email"

    login_response = session.post(login_url, data=login_data, allow_redirects=True)

    print(f"Login response status: {login_response.status_code}")

    if 'logout' in login_response.text.lower() or 'account' in login_response.url.lower():
        return session
    else:
        print("Login failed")
        return session


def get_top_200(index_main_area):
    pd.set_option('display.max_columns', None)
    top_routes = pd.read_csv('route-finder.csv')
    top_routes = top_routes[:200]

    top_routes = top_routes.drop(columns=['Avg Stars','Your Stars','Area Latitude','Area Longitude'], axis=1)

    top_routes[['Grade','Protection']] = top_routes['Rating'].str.split(' ', n=1, expand=True)
    top_routes = top_routes.drop(columns=['Rating'], axis=1)
    top_routes['Protection'] = top_routes['Protection'].fillna('G')

    top_routes['Route Type'] = top_routes['Route Type'].str.split(',').str[0]

    top_routes['Main Area'] = top_routes['Location'].str.split(' >').str[index_main_area]
    top_routes['Crag'] = top_routes['Location'].str.split('>').str[0]
    top_routes['Crag'] = top_routes['Crag'].str.split(r' - |\s*\(', regex=True).str[0].str.strip()

    top_routes = top_routes.drop(columns=['Location'], axis=1)

    return top_routes

def get_comments(object_id, session):
    comments_url = f"https://www.mountainproject.com/comments/forObject/Climb-Lib-Models-Route/{object_id}"
    comment_response = session.get(comments_url)
    comment_ajax = BeautifulSoup(comment_response.text, 'html.parser')
    comments = comment_ajax.find_all('div', class_='comment-body')
    comment_list = []

    for i in range(len(comments)):
        full_text = comments[i].find('span', id=lambda x: x and x.endswith('-full'))
        if full_text:
            comment_text = full_text.get_text(strip=True)
        else:
            comment_copy = comments[i]
            time_span = comment_copy.find('span', class_='comment-time')
            if time_span:
                time_span.decompose()
            comment_text = comment_copy.get_text(strip=True)

        comment_list.append(comment_text)

    return comment_list

def get_route_info(route_url, session):
    object_id = route_url.split('/')[4]

    route_page = BeautifulSoup(session.get(route_url).text, 'html.parser')
    route_info = route_page.find_all('div', class_='fr-view')
    desc = route_info[0].get_text(strip=True)
    if len(route_info) > 2:
        loc = route_info[1].get_text(strip=True)
        pro = route_info[2].get_text(strip=True)
    else:
        pro = route_info[1].get_text(strip=True)
        sidebar = route_page.find('div', class_='mp-sidebar')
        if sidebar:
            h3_tag = sidebar.find('h3')
            loc = h3_tag.get_text(strip=True)[10:] if h3_tag else None
        else:
            loc = 'N/A'

    comment_list = get_comments(object_id, session)

    return desc, loc, pro, comment_list

# Update tables

def db_upload_desc(db_session, route_id, desc, location, protection):
    new_entry = MpDescriptions(
        route_id=route_id,
        description=desc,
        location=location,
        protection=protection
    )
    db_session.add(new_entry)
    db_session.commit()
    logging.info(f"Added new description for route_id: {route_id}")

def db_upload_comments(db_session, route_id, comments):
    for comment_text in comments:
        new_comment = MpComments(
            route_id=route_id,
            comment_text=comment_text
        )
        db_session.add(new_comment)
    db_session.commit()
    logging.info(f"Added {len(comments)} new comment(s) for route_id: {route_id}")

def db_upload_lines(db_session, df):
    for index, row in df.iterrows():
        new_route = LegendaryLines(
            route_name = row['Route'],
            route_type = row['Route Type'],
            pitches = row['Pitches'],
            length = row['Length'],
            grade = row['Grade'],
            protection = row['Protection'],
            main_area = row['Main Area'],
            crag = row['Crag']
        )
        db_session.add(new_route)
    db_session.commit()
    logging.info(f"Uploaded {len(df)} lines for Legendary Lines Table")


if __name__ == '__main__':
    MP_ACCOUNT = os.getenv('MP_EMAIL')
    MP_PASSWORD = os.getenv('MP_PASSWORD')
    NEON_CONNECTION = os.getenv('NEON_URL')
    AREA_ID = '1'
    index_main_area = -3 # This is the index of the main area desired within the csv

    # For Example,
    # 'The Sentinel - West Face > The Sentinel > Real Hidden Valley > Hidden Valley Area > Joshua Tree National Park > California'
    # A Value of '-3' means the main area is 'Hidden Valley Area'. This is important depending on the area selected for all routes

    if not MP_ACCOUNT or not MP_PASSWORD:
        print("Error: Set MP_EMAIL and MP_PASSWORD in your .env file")
        exit(1)

    if not NEON_CONNECTION:
        print("Error: Set NEON_URL in your .env file")
        exit(1)

    engine, DbSession = init_db(NEON_CONNECTION)
    db_session = DbSession()

    session = create_authenticated_session(MP_ACCOUNT, MP_PASSWORD)

    if session:
        top_200 = get_top_200(index_main_area)
        db_upload_lines(db_session, top_200)
        for index, row in top_200.iterrows():
            route_url = row['URL']
            route_name = row['Route']

            description, location, protection, comments = get_route_info(route_url, session)
            print(f"Route Name: {route_name} \n")
            print("Route Description:", description, "\n")
            print("Location:", location, "\n")
            print("Protection:", protection, "\n")
            print(f"Total comments found: {len(comments)}\n")
            print(f"First comment: {comments[0]}\n")
            print(f"\n\n")

            route = db_session.query(ClimbingRoute).filter_by(route_name=route_name).first()
            if route is None:
                print(f"Route '{route_name}' not found in database, skipping...")
                continue
            route_id = route.id

            db_upload_desc(db_session, route_id, description, location, protection)
            db_upload_comments(db_session, route_id, comments)

            time.sleep(5)
    else:
        print("Failed to authenticate credentials.")
