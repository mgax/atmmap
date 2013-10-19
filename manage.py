#!/usr/bin/env python

import logging
import flask
from flask.ext.script import Manager
import requests
from path import path

logger = logging.getLogger(__name__)

BBOX = {'E': 26.25, 'N': 44.55, 'W': 25.95, 'S': 44.33}
DATA_URL = 'http://overpass.osm.rambler.ru/cgi/interpreter'
BANK_QUERY = ("[out:json];{filter}"
              "({BBOX[S]},{BBOX[W]},{BBOX[N]},{BBOX[E]});"
              "out;")
BRAND_DATA = flask.json.loads(
    (path(__file__).parent / 'brand_data.json')
    .text(encoding='utf-8')
)

views = flask.Blueprint('views', __name__)


@views.route('/')
def home():
    return flask.render_template('home.html', **{
        'bbox': BBOX,
        'center': {
            'lat': (BBOX['N'] + BBOX['S']) / 2,
            'lon': (BBOX['E'] + BBOX['W']) / 2,
        },
        'brands': [brand['code'] for brand in BRAND_DATA],
    })


def create_app():
    app = flask.Flask(__name__)
    app.debug = True
    app.register_blueprint(views)
    return app


def get_brand(node):
    name = (node['tags'].get('name', '') +
            node['tags'].get('operator', '')).lower()
    for brand in BRAND_DATA:
        if any(p in name for p in brand['patterns']):
            return brand['code']

    else:
        logger.warn("Can't figure out brand for %d: %r",
                    node['id'], node['tags'])
        return "?"


def get_nodes(query):
    resp = requests.get(DATA_URL, params={'data': query})
    for node in resp.json()['elements']:
        yield {
            'id': node['id'],
            'lat': node['lat'],
            'lon': node['lon'],
            'brand': get_brand(node),
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
    logging.basicConfig()
    create_manager(create_app()).run()
