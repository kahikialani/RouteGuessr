from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_dance.contrib.google import make_google_blueprint, google
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.mutable import MutableList
from datetime import date, datetime
import os
import logging


try:
    load_dotenv()
except Exception as e:
    print("python-dotenv not available")

map_api = os.getenv("MAPS_API_KEY")
cesium_key = os.getenv("CESIUM_KEY")
neon_connection = os.getenv("NEON_URL")

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = neon_connection
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to play Daily Challenge'

if os.getenv('RENDER') is None:
       os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

google_bp = make_google_blueprint(
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    scope=["openid", "https://www.googleapis.com/auth/userinfo.email",
           "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

# ======================= CLASSES =======================

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    google_id = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    daily_attempts = db.relationship('DailyAttempt', backref='user', lazy=True)

class DailyAttempt(db.Model):
    __tablename__ = 'daily_attempts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_date = db.Column(db.Date, db.ForeignKey('daily_route_data.challenge_date'), nullable=False)
    lat_guess = db.Column(MutableList.as_mutable(db.JSON))
    lon_guess = db.Column(MutableList.as_mutable(db.JSON))
    level_scores = db.Column(MutableList.as_mutable(db.JSON))
    total_score = db.Column(db.Integer)
    distance = db.Column(MutableList.as_mutable(db.JSON))
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'challenge_date', name='_user_date_uc'),)

class DailyRouteData(db.Model):
    __tablename__ = 'daily_route_data'
    id = db.Column(db.Integer, primary_key=True)
    challenge_date = db.Column(db.Date, nullable=False, unique=True)
    route_one_id = db.Column(db.Integer, db.ForeignKey('climbing_routes.id'), nullable=False)
    route_two_id = db.Column(db.Integer, db.ForeignKey('climbing_routes.id'), nullable=False)
    route_three_id = db.Column(db.Integer, db.ForeignKey('climbing_routes.id'), nullable=False)
    route_four_id = db.Column(db.Integer, db.ForeignKey('climbing_routes.id'), nullable=False)
    route_five_id = db.Column(db.Integer, db.ForeignKey('climbing_routes.id'), nullable=False)
    image_one_id = db.Column(db.Integer, db.ForeignKey('route_images.id'), nullable=False)
    image_two_id = db.Column(db.Integer, db.ForeignKey('route_images.id'), nullable=False)
    image_three_id = db.Column(db.Integer, db.ForeignKey('route_images.id'), nullable=False)
    image_four_id = db.Column(db.Integer, db.ForeignKey('route_images.id'), nullable=False)
    image_five_id = db.Column(db.Integer, db.ForeignKey('route_images.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships to access the actual route objects
    route_one = db.relationship('ClimbingRoute', foreign_keys=[route_one_id])
    route_two = db.relationship('ClimbingRoute', foreign_keys=[route_two_id])
    route_three = db.relationship('ClimbingRoute', foreign_keys=[route_three_id])
    route_four = db.relationship('ClimbingRoute', foreign_keys=[route_four_id])
    route_five = db.relationship('ClimbingRoute', foreign_keys=[route_five_id])

    # Relationships to access the actual image objects
    image_one = db.relationship('RouteImage', foreign_keys=[image_one_id])
    image_two = db.relationship('RouteImage', foreign_keys=[image_two_id])
    image_three = db.relationship('RouteImage', foreign_keys=[image_three_id])
    image_four = db.relationship('RouteImage', foreign_keys=[image_four_id])
    image_five = db.relationship('RouteImage', foreign_keys=[image_five_id])

class ClimbingArea(db.Model):
    __tablename__ = 'climbing_areas'
    id = db.Column(db.Integer, primary_key=True)
    area_name = db.Column(db.String(255), nullable=False, unique=True)
    area_link = db.Column(db.Text, nullable=False, unique=True)
    area_lat = db.Column(db.Float, nullable=False)
    area_lon = db.Column(db.Float, nullable=False)
    total_routes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    routes = db.relationship('ClimbingRoute', backref='climbing_area', lazy=True, cascade='all, delete-orphan')

class ClimbingRoute(db.Model):
    __tablename__ = 'climbing_routes'
    id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(255), nullable=False)
    route_link = db.Column(db.Text, nullable=False, unique=True)
    route_lat = db.Column(db.Float, nullable=False)
    route_lon = db.Column(db.Float, nullable=False)
    route_type = db.Column(db.String(255), nullable=False)
    route_grade = db.Column(db.String(255), nullable=False)
    route_stars = db.Column(db.Float, nullable=False)
    route_length = db.Column(db.Float, nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('climbing_areas.id', ondelete='CASCADE'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    images = db.relationship('RouteImage', backref='route', lazy=True, cascade='all, delete-orphan')

class RouteImage(db.Model):
    __tablename__ = 'route_images'
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('climbing_routes.id', ondelete='CASCADE'))
    image_link = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('route_id', 'image_link', name='_route_image_uc'),)

class Calculations:
    def __init__(self):
        self.user_data = {
            'user_lat': None,
            'user_lon': None
        }
        self.route_data = {
            'route_lat': None,
            'route_lon': None
        }

    def distance_finder(self, user_coords, route_coords):
        from geopy.distance import geodesic
        user_coords_list = [user_coords['user_lat'],user_coords['user_lon']]
        route_coords_list = [route_coords['route_lat'],route_coords['route_lon']]
        distance = geodesic(user_coords_list, route_coords_list)
        logging.debug(f"user_coords: {user_coords_list}, route_coords: {route_coords_list}")
        return distance.km

    def find_cesium_zoom(self, distance, fov = 30, padding = 2):
        from math import radians, sin, tan
        earth_radius = 6371
        fov_rad = radians(fov)

        half_distance = distance / 2
        central_angle = half_distance / earth_radius
        chord = 2 * earth_radius * sin(central_angle / 2)
        height_km = (chord / (2 * tan(fov_rad / 2))) * padding

        return height_km * 1000

    def find_score_daily(self, distance):
        from math import e
        scale = 300
        score = 5000 * (e **  (-10 * distance / scale))
        if score >= 4992:
            score = 5000
        return score

    def find_score_free_play(self, distance):
        from math import e
        score = 5000 * (e **  (-10 * distance / 30))
        if score >= 4990:
            score = 5000
        return score

    def get_score_class(self, score):
        """Return CSS class based on score (assuming max is 5000)"""
        if score >= 4500:
            return 'score-excellent'
        elif score >= 3000:
            return 'score-good'
        elif score >= 2000:
            return 'score-average'
        elif score >= 1000:
            return 'score-poor'
        else:
            return 'score-bad'

    def get_total_class(self, total):
        if total == 25000:
            return 'total-perfect'
        elif total >= 23000:
            return 'total-excellent'
        elif total >= 20000:
            return 'total-good'
        elif total >= 13000:
            return 'total-average'
        elif total >= 8000:
            return 'total-poor'
        else:
            return 'total-bad'

def generate_free_play(area_ids_input):
    from random import choice, choices

    all_area_ids = [int(area_id) for area_id in area_ids_input]
    area_ids = choices(all_area_ids, k=5)
    logging.debug(f"area_ids: {area_ids}")

    route_ids = []
    for area_id in area_ids:
        routes_in_area = [row.id for row in ClimbingRoute.query.filter_by(area_id=area_id).all()]
        route_ids.append(choice(routes_in_area))

    img_ids = []
    for route_id in route_ids:
        all_images = RouteImage.query.filter_by(route_id=route_id).all()
        image = choice(all_images)
        img_ids.append(image.id)

    # If only one area is selected, return that area's coordinates
    if len(all_area_ids) == 1:
        area = ClimbingArea.query.filter_by(id=all_area_ids[0]).first()
        area_lon = area.area_lon
        area_lat = area.area_lat
        zoom = 20000
    else:
        # For multiple areas, we'll need to calculate a center point or handle differently
        # For now, set to None and handle in the route
        area_lon = -103
        area_lat = 34
        zoom = 5999999

    data = {'area_ids': area_ids, 'route_ids': route_ids, 'img_ids': img_ids, 'area_lat': area_lat, 'area_lon': area_lon, 'zoom': zoom}
    return data

def generate_daily(entered_date = None):
    if entered_date is None:
        entered_date = date.today()
    existing = DailyRouteData.query.filter_by(challenge_date=entered_date).first()

    if existing:
        return existing

    from random import choices, choice
    all_area_ids = [row.id for row in ClimbingArea.query.all()]
    area_ids = choices(all_area_ids, k = 5)

    route_ids = []
    for area_id in area_ids:
        routes_in_area = [row.id for row in ClimbingRoute.query.filter_by(area_id=area_id).all()]
        route_ids.append(choice(routes_in_area))

    img_ids = []
    for route_id in route_ids:
        all_images = RouteImage.query.filter_by(route_id=route_id).all()
        image = choice(all_images)
        img_ids.append(image.id)

    new_daily = DailyRouteData(
        challenge_date=entered_date,
        route_one_id=route_ids[0],
        route_two_id=route_ids[1],
        route_three_id=route_ids[2],
        route_four_id=route_ids[3],
        route_five_id=route_ids[4],
        image_one_id=img_ids[0],
        image_two_id=img_ids[1],
        image_three_id=img_ids[2],
        image_four_id=img_ids[3],
        image_five_id=img_ids[4]
    )
    db.session.add(new_daily)
    db.session.commit()

    return new_daily


# ======================= FLASK DECORATORS =======================

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route("/")
@app.route("/home")
def home():
    session.clear()
    today = date.today()
    daily_completed = False
    if current_user.is_authenticated:
        attempt = DailyAttempt.query.filter_by(challenge_date=today, user_id = current_user.id).first()
        logging.debug(attempt)
        if attempt and len(attempt.level_scores) == 5:
            daily_completed = True

    return render_template("index.html",
                           daily_completed = daily_completed,
                           date=today,
                           user=current_user)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/terms")
def terms_page():
    return render_template("terms.html")
@app.route("/privacy")
def privacy_page():
    return render_template("privacy.html")



# Daily Section

@app.route("/daily")
@login_required
def daily():
    today = date.today()
    daily_data = DailyRouteData.query.filter_by(challenge_date=today).first()
    if not daily_data:
        generate_daily(entered_date=today)
        daily_data = DailyRouteData.query.filter_by(challenge_date=today).first()

    attempt = DailyAttempt.query.filter_by(
        user_id=current_user.id,
        challenge_date=today
    ).first()

    if attempt:
        if attempt.level_scores and len(attempt.level_scores) == 5:
            return redirect(url_for("daily_results"))


        completed_levels = len(attempt.level_scores) if attempt.level_scores else 0
        next_level = completed_levels + 1
    else:
        attempt = DailyAttempt(
            user_id=current_user.id,
            challenge_date=today,
            lat_guess=[],
            lon_guess=[],
            level_scores=[],
            distance=[],
            total_score=0
        )
        db.session.add(attempt)
        db.session.commit()
        next_level = 1
    return redirect(url_for('daily_level', level=next_level))

@app.route("/daily/level/<int:level>")
@login_required
def daily_level(level):
    if level < 1 or level > 5:
        return redirect(url_for("daily"))

    today = date.today()
    daily_data = DailyRouteData.query.filter_by(challenge_date=today).first()
    if not daily_data:
        return redirect(url_for('daily'))

    attempt = DailyAttempt.query.filter_by(
        user_id=current_user.id,
        challenge_date=today,
    ).first()

    if not attempt:
        return redirect(url_for("daily"))
    if len(attempt.level_scores) == 5:
        return redirect(url_for("daily_results", user=current_user))

    completed_levels = len(attempt.level_scores) if attempt.level_scores else 0

    if level <= completed_levels:
        return redirect(url_for("level_results", level = level))
    elif level > completed_levels + 1:
        return redirect(url_for("daily_level", level = completed_levels + 1))

    level_names = ["one","two","three","four","five"]
    level_name = level_names[level-1]

    image_id = getattr(daily_data, f"image_{level_name}_id")

    image_url = RouteImage.query.filter_by(id=image_id).first().image_link

    current_total = attempt.total_score if attempt.total_score else 0

    return render_template("daily_level.html",
                           level=level,
                           total_levels=5,
                           image_url=image_url,
                           current_total=current_total,
                           cesium_key=cesium_key)

@app.route("/daily/level/<int:level>/results")
@login_required
def level_results(level):
    today = date.today()

    attempt = DailyAttempt.query.filter_by(user_id=current_user.id, challenge_date=today).first()
    if not attempt:
        return redirect(url_for("daily"))

    daily_data = DailyRouteData.query.filter_by(challenge_date=today).first()
    if not daily_data:
        return redirect(url_for('daily'))

    level_idx0 = level - 1
    level_names = ["one","two","three","four","five"]
    level_name = level_names[level-1]

    route_id = getattr(daily_data, f"route_{level_name}_id")
    image_id = getattr(daily_data, f"image_{level_name}_id")

    image_url = RouteImage.query.filter_by(id=image_id).first().image_link
    route = ClimbingRoute.query.filter_by(id=route_id).first()

    # Attempt data to render
    score = attempt.level_scores[level_idx0]
    lat_guess = attempt.lat_guess[level_idx0]
    lon_guess = attempt.lon_guess[level_idx0]
    distance = attempt.distance[level_idx0]
    total_score = attempt.total_score

    # Route data to render
    route_name = route.route_name
    route_link = route.route_link
    route_lat = route.route_lat
    route_lon = route.route_lon
    route_type = route.route_type
    route_grade = route.route_grade
    route_stars = route.route_stars
    route_length = int(route.route_length)

    # Calculation data to render
    if distance >= 1:
        distance_str = f"{distance:.2f} km"
    else:
        distance_str = f"{distance*1000:.2f} m"

    avg_lat = (lat_guess + route_lat) / 2
    avg_lon = (lon_guess + route_lon) / 2

    # Area name finder
    area_name = ClimbingArea.query.filter_by(id=route.area_id).first().area_name

    if route_type == "TR":
        route_type_str = "Top Rope"
    elif route_type == "Trad":
        route_type_str = "Trad Climb"
    elif route_type == "Sport":
        route_type_str = "Sport Climb"
    elif route_type == "Boulder":
        route_type_str = "Boulder"
    else:
        route_type_str = "Unknown"

    stars = int(route_stars)
    if stars == 0:
        stars = "💣"
    elif stars <= 1.6:
        stars = "★☆☆☆"
    elif stars <= 2.6:
        stars = "★★☆☆"
    elif stars <= 3.6:
        stars = "★★★☆"
    else:
        stars = "★★★★"

    zoom = Calculations().find_cesium_zoom(distance)
    if zoom <= 3500:
        zoom = 3500

    return render_template("daily_result.html",
                           level=level,
                           cesium_key = cesium_key,
                           total_levels=5,
                           image_url=image_url,
                           score=score,
                           user_lat=lat_guess,
                           user_lon=lon_guess,
                           distance=distance,
                           current_total=total_score,
                           route_name=route_name.upper(),
                           route_link=route_link,
                           route_type=route_type_str,
                           route_grade=route_grade,
                           route_stars=route_stars,
                           stars=stars,
                           route_length=route_length,
                           route_lat=route_lat,
                           route_lon=route_lon,
                           distance_str=distance_str,
                           avg_lon=avg_lon,
                           avg_lat=avg_lat,
                           zoom=zoom,
                           area_name=area_name)

@app.route('/daily/results')
@login_required
def daily_results():
    today = date.today()

    attempt = DailyAttempt.query.filter_by(user_id=current_user.id, challenge_date=today).first()
    if not attempt or len(attempt.level_scores) < 5:
        return redirect(url_for("daily"))

    daily_data = DailyRouteData.query.filter_by(
        challenge_date=today
    ).options(
        db.joinedload(DailyRouteData.route_one).joinedload(ClimbingRoute.climbing_area),
        db.joinedload(DailyRouteData.route_two).joinedload(ClimbingRoute.climbing_area),
        db.joinedload(DailyRouteData.route_three).joinedload(ClimbingRoute.climbing_area),
        db.joinedload(DailyRouteData.route_four).joinedload(ClimbingRoute.climbing_area),
        db.joinedload(DailyRouteData.route_five).joinedload(ClimbingRoute.climbing_area),
        db.joinedload(DailyRouteData.image_one),
        db.joinedload(DailyRouteData.image_two),
        db.joinedload(DailyRouteData.image_three),
        db.joinedload(DailyRouteData.image_four),
        db.joinedload(DailyRouteData.image_five)
    ).first()

    if not daily_data:
        return redirect(url_for("daily"))

    level_data = {}
    level_names = ["one", "two", "three", "four", "five"]
    calc = Calculations()
    for i in range(1, 6):
        level_name = level_names[i - 1]
        route = getattr(daily_data, f"route_{level_name}")
        image = getattr(daily_data, f"image_{level_name}")
        level_data[str(i)] = {
            'route_name': route.route_name.upper(),
            'route_link': route.route_link,
            'route_grade': route.route_grade,
            'route_type': route.route_type,
            'route_stars': route.route_stars,
            'route_length': int(route.route_length),
            'route_lat': route.route_lat,
            'route_lon': route.route_lon,
            'area_name': route.climbing_area.area_name,
            'image_link': image.image_link,
            'score': attempt.level_scores[i - 1],
            'distance': attempt.distance[i - 1],
            'guess_lat': attempt.lat_guess[i - 1],
            'guess_lon': attempt.lon_guess[i - 1],
            'score_class': calc.get_score_class(attempt.level_scores[i - 1])
        }
    total_score_class = calc.get_total_class(attempt.total_score)

    return render_template("daily_end.html",
                           user=current_user,
                           total_score=attempt.total_score,
                           level_data=level_data,
                           total_score_class=total_score_class,
                           date=today)

@app.route("/leaderboard")
@app.route("/daily-leaderboard")
def daily_leaderboard():
    today = date.today()

    from sqlalchemy.orm import joinedload
    leaderboard = (DailyAttempt.query.filter_by(
        challenge_date=today
    ).filter(
        DailyAttempt.level_scores.isnot(None),
        db.func.json_array_length(DailyAttempt.level_scores) == 5
    ).options(
        joinedload(DailyAttempt.user)
    ).order_by(
        DailyAttempt.total_score.desc()
    ).all())

    return render_template("leaderboard.html",
                           leaderboard=leaderboard,
                           date=today,
                           current_user=current_user)

@app.route("/free-play/<path:area_names>")
def free_play(area_names):
    # area_names can be a single area or comma-separated list of areas
    # e.g., "/free-play/RedRocks" or "/free-play/RedRocks,Yosemite,JTree"
    area_names_list = [name.strip() for name in area_names.split(',')]

    data = generate_free_play(area_names_list)
    next_level = 1

    session['data'] = data
    session['level_scores'] = []
    session['guesses_lat'] = []
    session['guesses_lon'] = []
    session['distances'] = []
    session['level'] = next_level
    session['total_score'] = 0
    session['result_info'] = []

    return redirect(url_for("free_play_level", level=next_level))

@app.route("/free-play/level/<level>")
def free_play_level(level):
    # if not session.get('level_scores'):
    #     return redirect(url_for("free_play"))
    #
    # if not session.get('data'):
    #     return redirect(url_for("free_play"))
    #
    # if level != session.get('level'):
    #     return redirect(url_for("free_play_level", level=session.get('level')))
    #
    # if level > 5:
    #     return redirect(url_for("free_play_final_results"))

    # Structured like this data = {'area_ids': area_ids, 'route_ids': route_ids, 'img_ids': img_ids}
    data = session['data']
    image_id = data['img_ids'][int(level) - 1]
    image_url = RouteImage.query.filter_by(id=image_id).first().image_link

    # Get base coordinates - if multiple areas (None), calculate from the specific area
    base_lat = data.get('area_lat')
    base_lon = data.get('area_lon')
    zoom_level = data.get('zoom')


    total_score = session['total_score']
    logging.debug(session)
    return render_template("free_level.html",
                           base_lat = base_lat,
                           base_lon = base_lon,
                           image_url=image_url,
                           zoom_level=zoom_level,
                           total_levels=5,
                           level=level,
                           current_total=total_score,
                           cesium_key=cesium_key)

@app.route("/free-play/level/<int:level>/results")
def free_play_results(level):
    if not session:
        return redirect(url_for("free_play"))

    if len(session['level_scores']) != level:
        # TODO
        return redirect(url_for("free_play_level", level=level))
    data = session['data']
    image_id = data['img_ids'][int(level) - 1]
    route_id = data['route_ids'][int(level) - 1]
    area_id = data['area_ids'][int(level) - 1]

    image_info = RouteImage.query.filter_by(id=image_id).first()
    route_info = ClimbingRoute.query.filter_by(id=route_id).first()
    area_info = ClimbingArea.query.filter_by(id=area_id).first()

    logging.debug(session)
    distance = session['distances'][int(level) - 1]
    user_lon = session['guesses_lon'][int(level) - 1]
    user_lat = session['guesses_lat'][int(level) - 1]

    if distance >= 1:
        distance_str = f"{distance:.2f} km"
    else:
        distance_str = f"{distance*1000:.2f} m"

    route_lat = route_info.route_lat
    route_lon = route_info.route_lon

    avg_lat = (user_lat + route_lat) / 2
    avg_lon = (user_lon + route_lon) / 2

    score = session['level_scores'][int(level) - 1]
    total_score = session['total_score']

    if route_info.route_type == "TR":
        route_type_str = "Top Rope"
    elif route_info.route_type == "Trad":
        route_type_str = "Trad Climb"
    elif route_info.route_type == "Sport":
        route_type_str = "Sport Climb"
    elif route_info.route_type == "Boulder":
        route_type_str = "Boulder"
    else:
        route_type_str = "Unknown"

    stars = int(route_info.route_stars)
    if stars == 0:
        stars = "💣"
    elif stars <= 1.6:
        stars = "★☆☆☆"
    elif stars <= 2.6:
        stars = "★★☆☆"
    elif stars <= 3.6:
        stars = "★★★☆"
    else:
        stars = "★★★★"

    zoom = Calculations().find_cesium_zoom(distance)
    if zoom <= 3500:
        zoom = 3500
    logging.debug(f"Zoom height (in meters): {zoom}")

    result_info = session['result_info']
    result_info.append({
        'route_name': route_info.route_name,
        'route_grade': route_info.route_grade,
        'route_length': route_info.route_length,
        'route_type': route_info.route_type,
        'route_stars': route_info.route_stars,
        'route_link': route_info.route_link,
        'area_name': area_info.area_name,
        'stars_str': stars,
        'type_str': route_type_str,
        'img_url': image_info.image_link
    })
    session['result_info'] = result_info

    logging.debug(f"Session info: {session['result_info']}")
    logging.debug(f"Data: {session['data']}")
    logging.debug(f"Total Score: {session['total_score']}")
    logging.debug(f"Distances: {session['distances']}")
    logging.debug(f"Scores: {session['level_scores']}")
    logging.debug(f"Test: {session['result_info'][int(level) - 1]}")

    return render_template("free_result.html",
                           level=level,
                           cesium_key=cesium_key,
                           total_levels=5,
                           image_url = image_info.image_link,
                           score = score,
                           user_lat = user_lat,
                           user_lon = user_lon,
                           distance = session['distances'][int(level) - 1],
                           current_total = total_score,
                           route_name = route_info.route_name.upper(),
                           route_link = route_info.route_link,
                           route_type = route_type_str,
                           route_grade = route_info.route_grade,
                           route_stars = route_info.route_stars,
                           stars = stars,
                           route_length = route_info.route_length,
                           route_lat = route_info.route_lat,
                           route_lon = route_info.route_lon,
                           distance_str = distance_str,
                           avg_lon = avg_lon,
                           avg_lat = avg_lat,
                           zoom = zoom,
                           area_name = area_info.area_name)

@app.route('/free-play/results')
@login_required
def free_play_end():
    if not session:
        return redirect(url_for("free_play"))

    if len(session['level_scores']) != 5:
        # TODO
        return redirect(url_for("free_play"))


    calc = Calculations()
    level_data = {}
    for i in range(1, 6):
        logging.debug(f"TESTING: {session['result_info'][i-1]}")
        level_data[str(i)] = {
            'route_name': session['result_info'][i-1]['route_name'],
            'route_link': session['result_info'][i-1]['route_link'],
            'route_grade': session['result_info'][i-1]['route_grade'],
            'route_type': session['result_info'][i-1]['route_type'],
            'route_stars': session['result_info'][i-1]['route_stars'],
            'route_length': int(session['result_info'][i-1]['route_length']),
            'area_name': session['result_info'][i-1]['area_name'],
            'image_link': session['result_info'][i-1]['img_url'],
            'score': session['level_scores'][i-1],
            'score_class': calc.get_score_class(session['level_scores'][i - 1]),
            'stars_str': session['result_info'][i-1]['stars_str'],
            'type_str': session['result_info'][i-1]['type_str'],
            'distance': session['distances'][i-1]
        }
    total_score = session['total_score']
    total_score_class = calc.get_total_class(total_score)
    return render_template("free_end.html",
                           user=current_user,
                           total_score=session['total_score'],
                           total_score_class=total_score_class,
                           level_data=level_data)

@app.route('/classic')
def free_play_select():
    return render_template("free_select.html")


@app.route("/legendary-lines/play")
def legendary_lines_play():
    return render_template("legendary_lines_play.html")


# ======================= APIs =======================
@app.route("/api/submit-free-play", methods=["POST"])
def submit_free_play():
    json = request.get_json()
    level = json['level']
    guess_lat = json.get('guess_lat')
    guess_lon = json.get('guess_lon')

    # Check if this level has already been completed
    if len(session['level_scores']) >= int(level):
        # Level already completed, return existing score
        return jsonify({
            'success': True,
            'score': session['level_scores'][int(level) - 1],
            'distance': session['distances'][int(level) - 1],
            'total_score': session['total_score']
        })

    session['guesses_lat'].append(guess_lat)
    session['guesses_lon'].append(guess_lon)
    logging.debug(f"guess_lat: {guess_lat}, guess_lon: {guess_lon}, level: {level}")
    logging.debug(session)


    data = session['data']
    route_id = data['route_ids'][int(level) - 1]
    route_data = ClimbingRoute.query.filter_by(id=route_id).first()
    route_lat, route_lon = route_data.route_lat, route_data.route_lon

    calc = Calculations()
    user_coords = {
        'user_lat': guess_lat,
        'user_lon': guess_lon
    }

    route_coords = {
        'route_lat': route_lat,
        'route_lon': route_lon
    }

    distance = calc.distance_finder(user_coords, route_coords)
    score = calc.find_score_daily(distance)
    score = int(round(score))

    session['level_scores'].append(score)
    distances = session['distances']
    distances.append(distance)
    session['distances'] = distances

    # Update total score when guess is submitted, not on results page
    session['total_score'] = sum(session['level_scores'])

    return jsonify({
        'success': True,
        'score': int(score),
        'distance': distance,
        'total_score': session['total_score']
    })


@app.route("/api/submit-level", methods=["POST"])
@login_required
def submit_level():
    json = request.get_json()
    level = json["level"]
    guess_lat = json.get("guess_lat")
    guess_lon = json.get("guess_lon")
    today = date.today()

    # Query Route Data
    daily_data = DailyRouteData.query.filter_by(challenge_date=today).first()
    if not daily_data:
        return redirect(url_for("daily"))

    level_names = ["one","two","three","four","five"]
    level_name = level_names[level-1]

    route_id = getattr(daily_data, f"route_{level_name}_id")
    route = ClimbingRoute.query.filter_by(id=route_id).first()
    if not route:
        return redirect(url_for("home"))            # TODO

    # Query DailyAttempt
    attempt = DailyAttempt.query.filter_by(user_id=current_user.id, challenge_date=today).first()
    if not attempt:
        return redirect(url_for("home"))            # TODO

    completed_levels = len(attempt.level_scores) if attempt.level_scores else 0

    if level <= completed_levels:
        return redirect(url_for("level_results", level = level))
    elif level > completed_levels + 1:
        return redirect(url_for("daily_level", level = completed_levels + 1))

    # Compute Calculations
    calc = Calculations()
    user_coords = {
        'user_lat': guess_lat,
        'user_lon': guess_lon
    }

    route_coords = {
        'route_lat': route.route_lat,
        'route_lon': route.route_lon
    }

    distance = calc.distance_finder(user_coords, route_coords)
    score = calc.find_score_daily(distance)
    score = int(round(score))

    # Query New Data for DB Commit
    attempt.lat_guess.append(guess_lat)
    attempt.lon_guess.append(guess_lon)
    attempt.level_scores.append(score)
    attempt.total_score = sum(attempt.level_scores)
    attempt.distance.append(distance)

    db.session.commit()

    return jsonify({
        'success': True,
        'score': int(score),
        'distance': distance,
        'total_score': attempt.total_score
    })

# ======================= GOOGLE AUTHENTICATION =======================
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/google-login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    try:
        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            flash("Failed to fetch user info from Google")
            return redirect(url_for("login"))

        google_info = resp.json()
        google_id = google_info["id"]
        email = google_info["email"]
        username = google_info.get("name", email.split('@')[0])

        user = User.query.filter_by(google_id=google_id).first()

        if not user:
            user = User(
                google_id=google_id,
                email=email,
                username=username
            )
            db.session.add(user)
            db.session.commit()

        login_user(user, remember=True)
        return redirect(url_for("daily"))

    except Exception as e:
        logging.error(f"Google login error: {e}")
        flash("An error occurred during login")
        return redirect(url_for("login"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.cli.command()
def init_db():
    db.create_all()
    print("Database tables created!")

# ======================= ERROR HANDLING =======================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ======================= DEVELOPER FUNCTIONS =======================
@app.route("/reset-daily")
def reset_daily():
    today = date.today()
    attempt = DailyAttempt.query.filter_by(user_id=current_user.id, challenge_date=today).first()
    if attempt:
        db.session.delete(attempt)
        db.session.commit()
        return "Today's attempt deleted. <a href='/home'>Play again</a>"
    else:
        return "No attempt found in db. <a href='/home'>Play again</a>"


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if os.getenv('RENDER') is None:
        with app.app_context():
            db.create_all()
            print("Database initialized")
    app.run(host='0.0.0.0', port=8080, debug=True)