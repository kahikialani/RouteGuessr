from flask import Flask, render_template, request, jsonify, session
from route import FindRandomRoute
from waitress import serve
import threading
import uuid
import logging
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("MAPS_API_KEY")

app = Flask(__name__)
app.secret_key = 'random.uniform(0.0, 100.0)'
operations = {}

@app.route('/')
@app.route('/index')
def index():
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

@app.route('/results/<operation_id>')
def results(operation_id):
    if operation_id in operations and operations[operation_id]['status'] == 'complete':
        data = operations[operation_id]['data']
        session[f'results_{operation_id}'] = data
        del operations[operation_id]
        return render_template('results.html',
                               image_url = data['image_url'],
                               route_url = data['route_url'],
                               area_name = data['area_name'],
                               route_name = data['route_name'],
                               area_lat = data['area_lat'],
                               area_lon = data['area_lon'],
                               route_lat = data['route_lat'],
                               route_lon = data['route_lon'],
                               location = str(data['route_lat'] + data['area_lon']),
                               maps_key = api_key)
    elif f'results_{operation_id}' in session:
        data = session[f'results_{operation_id}']
        return render_template('results.html',
                               image_url = data['image_url'],
                               route_url = data['route_url'],
                               area_name = data['area_name'],
                               route_name = data['route_name'],
                               area_lat = data['area_lat'],
                               area_lon = data['area_lon'],
                               route_lat = data['route_lat'],
                               route_lon = data['route_lon'],
                               location = str(data['route_lat'] + data['area_lon']),
                               maps_key = api_key)
    else:
        return render_template('routes.html')

@app.route('/results')
def results_noargs():
    return render_template('routes.html')



@app.route('/submit_guess', methods = ['POST'])
def submit_guess():
    data = request.get_json()
    user_lat = data['lat']
    user_lng = data['lng']
    return jsonify({'status':'success'})

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    serve(app, host = "0.0.0.0", port = 8000)