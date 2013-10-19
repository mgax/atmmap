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
    return flask.render_template('home.html', **{
        'center': {
            'lat': (BBOX['N'] + BBOX['S']) / 2,
            'lon': (BBOX['E'] + BBOX['W']) / 2,
        },
    })


def create_app():
    app = flask.Flask(__name__)
    app.debug = True
    app.register_blueprint(views)
    return app


def get_nodes(query):
    resp = requests.get(DATA_URL, params={'data': query})
    for elem in resp.json()['elements']:
        yield {
            'id': elem['id'],
            'lat': elem['lat'],
            'lon': elem['lon'],
            'name': elem['tags'].get('name'),
        }


def create_manager(app):
    manager = Manager(app)

    @manager.command
    def download():
        bank_query = BANK_QUERY.format(
            BBOX=BBOX,
            filter="node[amenity=bank][atm=yes]",
        )
        atm_query = BANK_QUERY.format(
            BBOX=BBOX,
            filter="node[amenity=atm]",
        )

        data = list(get_nodes(bank_query)) + list(get_nodes(atm_query))

        data_path = app.static_folder + '/data.json'
        with open(data_path, 'w', encoding='utf-8') as f:
            flask.json.dump(data, f, indent=2, sort_keys=True)

    return manager


if __name__ == '__main__':
    create_manager(create_app()).run()
