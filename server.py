from flask import Flask, render_template, request
from route import FindRandomRoute
from waitress import serve

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/route')
def find_route():
    area = request.args.get('route')
    route_data = FindRandomRoute().get_area(area)
    return render_template("routes.html",
                           imageurl = route_data[0],
                           location = route_data[2],
                           page = route_data[1])

@app.route('/play')
def play():
    return render_template('play.html')

if __name__ == '__main__':
    print('init')
    serve(app, host = "0.0.0.0", port = 8000)