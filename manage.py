#!/usr/bin/env python

import flask
from flask.ext.script import Manager
import requests

BBOX = {'E': 26.11, 'N': 44.45, 'W': 26.07, 'S': 44.42}
DATA_URL = 'http://overpass.osm.rambler.ru/cgi/interpreter'
BANK_QUERY = ("[out:json];{filter}"
              "({BBOX[S]},{BBOX[W]},{BBOX[N]},{BBOX[E]});"
              "out;")

views = flask.Blueprint('views', __name__)


@views.route('/')
def home():
    return ':)'


def create_app():
    app = flask.Flask(__name__)
    app.register_blueprint(views)
    return app


def create_manager(app):
    manager = Manager(app)

    @manager.command
    def download():
        query = BANK_QUERY.format(
            BBOX=BBOX,
            filter="node[amenity=bank][atm=yes]",
        )
        resp = requests.get(DATA_URL, params={'data': query})

        data = []
        for elem in resp.json()['elements']:
            data.append({
                'lat': elem['lat'],
                'lon': elem['lon'],
                'name': elem['tags'].get('name'),
            })

        data_path = app.static_folder + '/data.json'
        with open(data_path, 'w', encoding='utf-8') as f:
            flask.json.dump(data, f, indent=2, sort_keys=True)

    return manager


if __name__ == '__main__':
    create_manager(create_app()).run()
