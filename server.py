from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from route import FindRandomRoute, Calculations
from waitress import serve
import threading
import uuid
import logging
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded .env file for local development")
except ImportError:
    print("python-dotenv not available (production environment)")
    pass

api_key = os.getenv("MAPS_API_KEY")

app = Flask(__name__)
app.secret_key = 'secret_secret'
operations = {}

@app.route('/')
@app.route('/index')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/area')
def loading_page_query():
    logging.debug(request.args.get('area'))
    area = request.args.get('area')

    operation_id = str(uuid.uuid4())
    operations[operation_id] = {
        'status': 'processing',
        'data' : None,
        'error': None
    }

    thread = threading.Thread(target=process_area, args=(operation_id, area))
    thread.daemon = True
    thread.start()

    return render_template('loading.html', operation_id = operation_id)

def process_area(operation_id, area):
    try:
        route_data = FindRandomRoute().get_area(area)
        operations[operation_id] = {
            'status': 'complete',
            'data': {
                'image_url': route_data['image_url'],
                'route_url': route_data['route_url'],
                'starting_url': route_data['starting_url'],
                'route_name': route_data['route_name'],
                'area_name': route_data['area_name'],
                'area_lat': route_data['area_lat'],
                'area_lon': route_data['area_lon'],
                'route_lat': route_data['route_lat'],
                'route_lon': route_data['route_lon'],
            },
            'error': None
        }
    except Exception as e:
        operations[operation_id] = {
            'status': 'error',
            'data': None,
            'error': str(e)
        }

@app.route('/check_status/<operation_id>')
def check_status(operation_id):
    if operation_id in operations:
        return jsonify(operations[operation_id])
    else:
        return jsonify({'status': 'not_found', 'data': None, 'error': 'Operation not found'})

@app.route('/route/<operation_id>', methods = ["POST", "GET"])
def route(operation_id):
    session_key = f"route_{operation_id}"
    if operation_id in operations and operations[operation_id]['status'] == 'complete':
        data = operations[operation_id]['data']
        if session_key not in session:
            session[session_key] = data
            del operations[operation_id]
        else:
            existing_data = session[session_key]
            for key, value in data.items():
                if key not in existing_data:
                    existing_data[key] = value
            session[session_key] = existing_data
            del operations[operation_id]
        data = session[session_key]
        return render_template('route.html',
                               image_url = data['image_url'],
                               route_url = data['route_url'],
                               area_name = data['area_name'],
                               route_name = data['route_name'],
                               area_lat = data['area_lat'],
                               area_lon = data['area_lon'],
                               route_lat = data['route_lat'],
                               route_lon = data['route_lon'],
                               location = str(data['route_lat'] + data['area_lon']),
                               maps_key = api_key,
                               operation_id=operation_id)
    elif session_key in session:
        data = session[session_key]
        return render_template('route.html',
                               image_url = data['image_url'],
                               route_url = data['route_url'],
                               area_name = data['area_name'],
                               route_name = data['route_name'],
                               area_lat = data['area_lat'],
                               area_lon = data['area_lon'],
                               route_lat = data['route_lat'],
                               route_lon = data['route_lon'],
                               location = str(data['route_lat'] + data['area_lon']),
                               maps_key = api_key,
                               operation_id=operation_id)
    else:
        return redirect(url_for('index'))



@app.route('/submit-guess/<operation_id>', methods=['POST'])
def submit_guess(operation_id):
    try:
        session_key = f"route_{operation_id}"
        if session_key not in session:
            logging.error(f"No session data found for {session_key}")
            return redirect(url_for('index'))
        user_lat = float(request.form['lat'])
        user_lon = float(request.form['lng'])
        route_data = session[session_key].copy()
        route_data['user_lat'] = user_lat
        route_data['user_lon'] = user_lon
        session[session_key] = route_data
        session.modified = True
        return redirect(url_for('single_result', operation_id = operation_id))
    except Exception as e:
        logging.error(f"Error in submit_guess: {str(e)}")
        return redirect(url_for('index'))

@app.route('/single-result/<operation_id>')
def single_result(operation_id):
    session_key = f"route_{operation_id}"

    if session_key in session:
        data = session[session_key]
        logging.debug(f'Found session data with keys: {list(data.keys())}')
        user_coords = {
            'user_lat': session[f'route_{operation_id}']['user_lat'],
            'user_lon': session[f'route_{operation_id}']['user_lon']
        }
        route_coords = {
            'route_lat': session[f'route_{operation_id}']['route_lat'],
            'route_lon': session[f'route_{operation_id}']['route_lon']
        }
        avg_coords = {
            'avg_lat': (user_coords['user_lat'] + route_coords['route_lat'])/2,
            'avg_lon': (user_coords['user_lon'] + route_coords['route_lon'])/2
        }

        calculator = Calculations()
        distance = calculator.distance_finder(user_coords, route_coords)
        zoom_level = 12
        if distance < 0.8:
            zoom_level = 17
        if distance < 1.0:
            zoom_level = 16
        elif distance < 3:
            zoom_level = 14
        elif distance < 5:
            zoom_level = 13
        elif distance < 10:
            zoom_level = 13
        elif distance < 20:
            zoom_level = 12
        elif distance < 40:
            zoom_level = 11
        elif distance < 80:
            zoom_level = 10
        elif distance < 150:
            zoom_level = 8
        else:
            zoom_level = 4
        logging.debug(f"zoom_level: {zoom_level}")
        logging.debug(f"distance: {distance}")

        data = session[f'route_{operation_id}']
        return render_template('single_result.html',
                               image_url=data['image_url'],
                               route_url=data['route_url'],
                               area_name=data['area_name'],
                               route_name=data['route_name'],
                               area_lat=data['area_lat'],
                               area_lon=data['area_lon'],
                               route_lat=data['route_lat'],
                               route_lon=data['route_lon'],
                               user_lat=data['user_lat'],
                               user_lon=data['user_lon'],
                               avg_lat=avg_coords['avg_lat'],
                               avg_lon=avg_coords['avg_lon'],
                               maps_key=api_key,
                               operation_id=operation_id,
                               zoom_level=zoom_level,
                               distance=distance)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    serve(app, host = "0.0.0.0", port = 8000)
