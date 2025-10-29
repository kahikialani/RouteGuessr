import pandas as pd

def find_top_routes():
    route_finder = pd.read_csv('route-finder.csv')
    routes = route_finder.head(100)
    print(routes)

if __name__ == '__main__':
    find_top_routes()
