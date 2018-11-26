# A.Piskun
# 24/11/2018
#
import os
from telegram import Location
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
    user_data = bot_tools.init_new_location(user_data, Location(20.4, 57.9))
    reply = Reply(user_data, 'location')
    assert reply.n_sights == 0
    assert reply.sight is None
    assert reply.markup.remove_keyboard is True


def test_sight_location_reply():
    user_data = bot_tools.init_user_data({})
    user_data = bot_tools.init_new_location(user_data, Location(37.620948, 55.688832))
    reply = Reply(user_data, 'location')
    assert reply.n_sights == config.get('max_next_events') + 1
    assert len(reply.markup.keyboard[0]) >= 2
    assert len(reply.markup.keyboard[1]) == 1


def test_history_location_reply():
    user_data = bot_tools.init_user_data({})
    user_data = bot_tools.init_new_location(user_data, Location(-0.09531, 51.521681))
    reply = Reply(user_data, 'location')
    assert reply.history is not None
    assert reply.n_sights == config.get('max_next_events') + 1
    assert len(reply.markup.keyboard[0]) == 3
    assert len(reply.markup.keyboard[1]) == 1


def test_max_next_reply():
    user_data = bot_tools.init_user_data({})
    user_data = bot_tools.init_new_location(user_data, Location(-0.09531, 51.521681))
    user_data['next'] = config.get('max_next_events') + 1
    reply = Reply(user_data, 'next')
    assert len(reply.markup.keyboard) == 1
    assert len(reply.markup.keyboard[0]) == 1
    button = reply.markup.keyboard[0][0]
    assert button.request_location is True


def test_last_next_reply():
    user_data = bot_tools.init_user_data({})
    user_data = bot_tools.init_new_location(user_data, Location(-0.09531, 51.521681))
    user_data['sights'] = user_data['sights'][:3]
    user_data['next'] = 2
    reply = Reply(user_data, 'next')
    assert len(reply.markup.keyboard[0]) >= 2
    assert len(reply.markup.keyboard[1]) == 1

    user_data['next'] = 3
    reply = Reply(user_data, 'next')
    assert len(reply.markup.keyboard) == 1
    assert len(reply.markup.keyboard[0]) == 1
    button = reply.markup.keyboard[0][0]
    assert button.request_location is True


def test_show_map_reply():
    user_data = bot_tools.init_user_data({})
    user_data = bot_tools.init_new_location(user_data, Location(-0.09531, 51.521681))
    reply = Reply(user_data, 'show_map')
    assert reply.location is not None
    assert isinstance(reply.location.latitude, float) is True
    assert isinstance(reply.location.longitude, float) is True


