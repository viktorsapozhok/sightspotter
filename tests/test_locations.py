# A.Piskun
# 11/11/2018
#
from telegram import Location
import config
import bot_tools
from constants import PATHS

config.init_from_json(PATHS['to_config'])


def test_remote_location():
    user_data = bot_tools.init_user_data({})
    config.set('max_distance', 10)
    sights, _ = bot_tools.find_nearest_sights(user_data['db'], Location(20.4, 57.9))
    assert len(sights) == 0


def test_sight_location():
    user_data = bot_tools.init_user_data({})
    sights, _ = bot_tools.find_nearest_sights(user_data['db'], Location(37.620948, 55.688832))
    assert sights[0][0] == 0


def test_sight_history():
    user_data = bot_tools.init_user_data({})
    _, history = bot_tools.find_nearest_sights(user_data['db'], Location(-0.09531, 51.521681))
    assert len(history[0][0][1]) > 1000


