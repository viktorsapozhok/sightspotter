# A.Piskun
# 24/11/2018
#
# running tests from command line:
#       sightspotter> python -m pytest tests/
#
import os
import config
import bot_tools
from bot_replies import Reply
from constants import PATHS

config.init_from_json(PATHS['to_config'])


def test_tokens():
    for var in ['SSB_TOKEN', 'SSB_TEST_TOKEN']:
        token = os.environ[var]
        prefix = token.split(':')[0]
        assert prefix.isdigit()
        assert len(prefix) == 9


def test_start_reply():
    user_data = bot_tools.init_user_data({})
    reply = Reply(user_data, 'start')
    button = reply.markup.keyboard[0][0]
    assert button.request_location is True


def test_remote_location_reply():
    user_data = bot_tools.init_user_data({})
    user_data = bot_tools.init_new_location(user_data, get_location(57.9, 20.4))
    reply = Reply(user_data, 'location')
    assert reply.n_sights == 0
    assert reply.sight is None
    assert reply.markup.remove_keyboard is True


def test_sight_location_reply():
    user_data = bot_tools.init_user_data({})
    user_data = bot_tools.init_new_location(user_data, get_location(55.688832, 37.620948))
    reply = Reply(user_data, 'location')
    assert reply.n_sights == config.get('max_next_events') + 1
    assert len(reply.markup.keyboard[0]) == 2
    assert len(reply.markup.keyboard[1]) == 1


def test_history_location_reply():
    user_data = bot_tools.init_user_data({})
    user_data = bot_tools.init_new_location(user_data, get_location(51.521681, -0.09531))
    reply = Reply(user_data, 'location')
    assert reply.history is not None
    assert reply.n_sights == config.get('max_next_events') + 1
    assert len(reply.markup.keyboard[0]) == 3
    assert len(reply.markup.keyboard[1]) == 1


def test_max_next_reply():
    user_data = bot_tools.init_user_data({})
    user_data = bot_tools.init_new_location(user_data, get_location(51.521681, -0.09531))
    user_data['next'] = config.get('max_next_events') + 1
    reply = Reply(user_data, 'next')
    assert len(reply.markup.keyboard) == 1
    assert len(reply.markup.keyboard[0]) == 1
    button = reply.markup.keyboard[0][0]
    assert button.request_location is True


def get_location(latitude, longitude):
    class Location(object):
        def __init__(self):
            self.latitude = latitude
            self.longitude = longitude
    return Location()




