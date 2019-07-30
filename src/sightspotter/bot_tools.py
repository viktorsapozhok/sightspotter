
import re
import numpy as np

from sightspotter import config
from sightspotter import dbhelper


def init_user_data(user_data):
    user_data['db'] = dbhelper.DBHelper(config.path_to_db)
    user_data['sights'] = None
    user_data['history'] = None
    user_data['location'] = None
    user_data['next'] = 0
    return user_data


def init_new_location(user_data, location):
    user_data['location'] = location
    user_data['next'] = 0
    user_data['sights'], user_data['history'] = find_nearest_sights(user_data['db'], location)
    return user_data


def is_initialized(user_data):
    if 'next' in user_data:
        return True
    return False


def get_state(user_data):
    if 'next' in user_data:
        if user_data['next'] > 0:
            return config.states['next']
    return config.states['location']


def add_user_log(db, user_name, action):
    db.add_user_log(user_name, action)


def find_nearest_sights(db, location):
    max_dist = config.max_dist
    #define latitude and longitude estimated intervals where we need to find sights
    d_lat = get_latitude_delta(location, max_dist)
    d_lon = get_longitude_delta(location, max_dist)

    #select sights from coordinates square area (upper estimate)
    sights = db.select_sights_between(
        location.latitude - (0.5 * d_lat), location.latitude + (0.5 * d_lat),
        location.longitude - (0.5 * d_lon), location.longitude + (0.5 * d_lon))
    history = []

    if len(sights) > 0:
        #distances between user_location and sights
        dist = [get_distance(s[1], s[2], location) for s in sights]
        #number of sights we can run through using next
        n_sights = config.n_next + 1
        indexes = [i for i in range(0, n_sights) if i < len(sights)]
        sorted_indexes = np.argsort(dist)[indexes]
        sight_idx = [sights[i][0] for i in sorted_indexes]
        sights = [sights[i] for i in sorted_indexes]
        history = [db.select_history(i) for i in sight_idx]
    return sights, history


def get_distance(lat, lon, location):
    lat1 = np.radians(lat)
    lon1 = np.radians(lon)
    lat2 = np.radians(location.latitude)
    lon2 = np.radians(location.longitude)
    d_lat = lat1 - lat2
    d_lon = lon1 - lon2
    a = np.sin(d_lat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(d_lon / 2)**2
    return 6373.0 * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def get_latitude_delta(location, distance):
    dist = get_distance(location.latitude + 0.1, location.longitude, location)
    return 0.1 * distance / dist


def get_longitude_delta(location, distance):
    dist = get_distance(location.latitude, location.longitude + 0.1, location)
    return 0.1 * distance / dist


def get_config_message(msg):
    text = ''
    for line in msg:
        text += line
    return text


def get_pattern(str):
    return re.compile('^(' + str + ')$', re.I)




