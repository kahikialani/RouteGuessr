from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_dance.contrib.google import make_google_blueprint, google
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableList
from datetime import date, datetime
import os
import logging


try:
    load_dotenv()
except Exception as e:
    print("python-dotenv not available")

map_api = os.getenv("MAPS_API_KEY")
neon_connection = os.getenv("NEON_URL")

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

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

    def find_score_daily(self, distance):
        from math import e
        score = 5000 * (e **  (-10 * distance / 300))
        if score >= 4995:
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
        elif score >= 3500:
            return 'score-good'
        elif score >= 2500:
            return 'score-average'
        elif score >= 1500:
            return 'score-poor'
        else:
            return 'score-bad'

    def get_total_class(self, total):
        if total == 25000:
            return 'total-perfect'
        elif total >= 24000:
            return 'total-excellent'
        elif total >= 21000:
            return 'total-good'
        elif total >= 19000:
            return 'total-average'
        elif total >= 14000:
            return 'total-poor'
        else:
            return 'total-bad'

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
    return render_template("home_page.html", user=current_user)

@app.after_request
def add_cache_headers(response):
    # Cache static files
    if request.path.startswith('/static/'):
        # Images get long cache
        if any(request.path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        # CSS and JS get medium cache with revalidation
        elif any(request.path.endswith(ext) for ext in ['.css', '.js']):
            response.headers['Cache-Control'] = 'public, max-age=86400, must-revalidate'
        # Fonts get long cache
        elif any(request.path.endswith(ext) for ext in ['.woff', '.woff2', '.ttf', '.otf']):
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    return response


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

    return render_template("daily_level.html",
                           level=level,
                           total_levels=5,
                           image_url=image_url,
                           current_total=0,
                           maps_key=map_api)

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

    if distance < 0.8:
        zoom_level = 16
    elif distance < 1.0:
        zoom_level = 16
    elif distance < 3:
        zoom_level = 14
    elif distance < 5:
        zoom_level = 13
    elif distance < 10:
        zoom_level = 12
    elif distance < 20:
        zoom_level = 11
    elif distance < 40:
        zoom_level = 10
    elif distance < 80:
        zoom_level = 9
    elif distance < 150:
        zoom_level = 8
    else:
        zoom_level = 4

    # Area name finder
    area_name = ClimbingArea.query.filter_by(id=route.area_id).first().area_name




    return render_template("daily_level_results.html",
                           level=level,
                           maps_key=map_api,
                           total_levels=5,
                           image_link=image_url,
                           score=score,
                           user_lat=lat_guess,
                           user_lon=lon_guess,
                           distance=distance,
                           total_score=total_score,
                           route_name=route_name,
                           route_link=route_link,
                           route_type=route_type,
                           route_grade=route_grade,
                           route_stars=route_stars,
                           route_length=route_length,
                           route_lat=route_lat,
                           route_lon=route_lon,
                           distance_str=distance_str,
                           avg_lon=avg_lon,
                           avg_lat=avg_lat,
                           zoom_level=zoom_level,
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
            'route_name': route.route_name,
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

    return render_template("daily_final_results.html",
                           user=current_user,
                           total_score=attempt.total_score,
                           level_data=level_data,
                           total_score_class=total_score_class,
                           date=today)

@app.route("/daily-leaderboard")
def daily_leaderboard():
    today = date.today()

    from sqlalchemy.orm import joinedload
    leaderboard = (DailyAttempt.query.filter_by(
        challenge_date=today
    ).options(
        joinedload(DailyAttempt.user)
    ).order_by(
        DailyAttempt.score.desc()
    ).limit(100).all()

    return render_template("leaderboard.html",
                           leaderboard=leaderboard,
                           date=today,
                           user=current_user)



# ======================= APIs =======================

@app.route("/api/submit-level", methods=["POST"])
@login_required
def submit_level():
    data = request.get_json()
    level = data["level"]
    guess_lat = data.get("guess_lat")
    guess_lon = data.get("guess_lon")
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
        return redirect(url_for("home"))            # Change before deployment

    # Query DailyAttempt
    attempt = DailyAttempt.query.filter_by(user_id=current_user.id, challenge_date=today).first()
    if not attempt:
        return redirect(url_for("home"))            # Change before deployment

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