import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

PATHS = {
    'to_config': os.path.join(ROOT_DIR, 'config.json'),
    'to_db': os.path.join(ROOT_DIR, 'db', 'sightspotter.db')
}

#conversation states
STATES = {
    'location': 0,
    'next': 1
}