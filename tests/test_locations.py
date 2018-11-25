# A.Piskun
# 11/11/2018
#
# running tests from command line:
#       sightspotter> python -m pytest tests/
#
import config
import bot_tools
from constants import PATHS

config.init_from_json(PATHS['to_config'])


def test_remote_location():
    user_data = bot_tools.init_user_data({})
    location = get_location(57.9, 20.4)
    config.set('max_distance', 10)
    sights, _ = bot_tools.find_nearest_sights(user_data['db'], location)
    assert len(sights) == 0


def test_sight_location():
    user_data = bot_tools.init_user_data({})
    location = get_location(55.688832, 37.620948)
    sights, _ = bot_tools.find_nearest_sights(user_data['db'], location)
    assert sights[0][0] == 0


def test_sight_history():
    user_data = bot_tools.init_user_data({})
    location = get_location(51.521681, -0.09531)
    _, history = bot_tools.find_nearest_sights(user_data['db'], location)
    assert len(history[0][0][1]) > 1000


def get_location(latitude, longitude):
    class Location(object):
        def __init__(self):
            self.latitude = latitude
            self.longitude = longitude
    return Location()
