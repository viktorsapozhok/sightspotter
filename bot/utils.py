# -*- coding: utf-8 -*-

"""Utilities
"""
from datetime import datetime
import logging
import re
from typing import Any, Dict

import numpy as np

from . import config

logger = logging.getLogger('sightspotter')
commuter = config.get_commuter()


def command_pattern(cmd):
    return re.compile('^(' + cmd + ')$', re.I)


def get_sights_count(sights):
    if sights is None:
        return 0
    else:
        return len(sights)


def get_user_data(location=None):
    data = dict()  # type: Dict[str, Any]
    data['next'] = 0
    data['location'] = None
    data['sights'] = None
    data['history'] = None

    if location is not None:
        data['location'] = location
        data['sights'], data['history'] = get_sights(location)

    return data


def get_sights(location):
    # find area from where we need to select sights
    lat_1, lat_2 = get_lat_interval(location, config.max_dist)
    lon_1, lon_2 = get_lon_interval(location, config.max_dist)

    # select sights from found area
    sights = select_sights_from_area(lat_1, lat_2, lon_1, lon_2)

    history = []

    if len(sights) > 0:
        # calculate distances between user location and each sight
        distances = [get_distance(s[1], s[2], location) for s in sights]

        # select closest sights
        n_sights = config.n_next + 1
        indexes = [i for i in range(0, n_sights) if i < len(sights)]
        sorted_indexes = np.argsort(distances)[indexes]
        sight_idx = [sights[i][0] for i in sorted_indexes]
        sights = [sights[i] for i in sorted_indexes]

        # select history for each selected sight
        history = [select_history(i) for i in sight_idx]

    return sights, history


def select_sights_from_area(lat_1, lat_2, lon_1, lon_2):
    sql = f"""
    SELECT
        sight_id, lat, lon, address, description, quest, answer, year
    FROM
        sights
    WHERE
        lat BETWEEN {lat_1} AND {lat_2} AND
        lon BETWEEN {lon_1} AND {lon_2}
    """

    df = commuter.select(sql)

    return df.values.tolist()


def select_history(sight_id):
    sql = f"""
    SELECT
        sight_id, history
    FROM
        history
    WHERE
        sight_id={sight_id}
    """

    df = commuter.select(sql)

    return df.values.tolist()


def get_lat_interval(location, distance):
    dist = get_distance(
        lat=location.latitude + 0.1,
        lon=location.longitude,
        location=location)

    delta = 0.1 * distance / dist
    lat_1 = location.latitude - (0.5 * delta)
    lat_2 = location.latitude + (0.5 * delta)

    return lat_1, lat_2


def get_lon_interval(location, distance):
    dist = get_distance(
        lat=location.latitude,
        lon=location.longitude + 0.1,
        location=location)

    delta = 0.1 * distance / dist
    lon_1 = location.longitude - (0.5 * delta)
    lon_2 = location.longitude + (0.5 * delta)

    return lon_1, lon_2


def get_distance(lat, lon, location):
    lat1 = np.radians(lat)
    lon1 = np.radians(lon)

    lat2 = np.radians(location.latitude)
    lon2 = np.radians(location.longitude)

    d_lat = lat1 - lat2
    d_lon = lon1 - lon2

    a = np.sin(d_lat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(d_lon / 2)**2

    return 6373.0 * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def is_user_data_initialized(user_data):
    if 'next' in user_data:
        return True
    return False


def get_state(user_data):
    if 'next' in user_data:
        if user_data['next'] > 0:
            return config.states['next']

    return config.states['location']


def write_log(user_name, user_log):
    logger.info(f'{user_name}: {user_log}')

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    commuter.execute(
        'insert into user_log values (?, ?, ?)',
        vars=(date, user_name, user_log))
