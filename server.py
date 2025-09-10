from flask import Flask, render_template, request
from route import FindRandomRoute
from waitress import serve

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/area')
def area_to_route():
    area = request.args.get('area')
    route_data = FindRandomRoute().get_area(area)
    return render_template("results.html",
                           imageurl = route_data[0],
                           page = route_data[1],
                           location = route_data[2])

@app.route('/results')
def results_noargs():
    return render_template('no_results.html')

if __name__ == '__main__':
    print('init')
    serve(app, host = "0.0.0.0", port = 4036)