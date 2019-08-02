# -*- coding: utf-8 -*-

import pytest

from telegram import Location

from sightspotter import config
from sightspotter import callbacks, replies, utils


@pytest.fixture(scope='module')
def context():
    class Context(object):
        user_data = dict()

    return Context()


def test_tokens():
    for token in [config.token, config.test_token]:
        prefix = token.split(':')[0]

        assert prefix.isdigit()
        assert len(prefix) == 9


def test_start_reply():
    reply = replies.StartReply(utils.get_user_data())
    button = reply.markup.keyboard[0][0]

    assert button.request_location is True


def test_not_found_reply(context):
    context.user_data = utils.get_user_data(Location(20.4, 57.9))
    reply = callbacks.Location().create_reply(context)

    assert reply.__class__.__name__ == 'NotFoundReply'


def test_sight_reply(context):
    context.user_data = utils.get_user_data(Location(37.620948, 55.688832))
    reply = callbacks.Location().create_reply(context)

    assert reply.__class__.__name__ == 'SightReply'
    assert len(reply.markup.keyboard[0]) >= 2
    assert len(reply.markup.keyboard[1]) == 1


def test_history_location_reply(context):
    context.user_data = utils.get_user_data(Location(-0.09531, 51.521681))
    reply = callbacks.Location().create_reply(context)

    assert reply.__class__.__name__ == 'SightReply'
    assert len(reply.history) > 0
    assert len(reply.markup.keyboard[0]) == 3
    assert len(reply.markup.keyboard[1]) == 1


def test_max_next_reply(context):
    context.user_data = utils.get_user_data(Location(-0.09531, 51.521681))
    context.user_data['next'] = config.n_next + 1
    reply = callbacks.NextSight().create_reply(context)
    button = reply.markup.keyboard[0][0]

    assert reply.__class__.__name__ == 'MaxNextEventsReply'
    assert len(reply.markup.keyboard) == 1
    assert len(reply.markup.keyboard[0]) == 1
    assert button.request_location is True


def test_last_next_reply(context):
    context.user_data = utils.get_user_data(Location(-0.09531, 51.521681))
    context.user_data['sights'] = context.user_data['sights'][:3]
    context.user_data['next'] = 2
    reply = callbacks.NextSight().create_reply(context)

    assert reply.__class__.__name__ == 'SightReply'
    assert len(reply.markup.keyboard[0]) >= 2
    assert len(reply.markup.keyboard[1]) == 1

    context.user_data['next'] = 3
    reply = callbacks.NextSight().create_reply(context)
    button = reply.markup.keyboard[0][0]

    assert reply.__class__.__name__ == 'NextNotFoundReply'
    assert len(reply.markup.keyboard) == 1
    assert len(reply.markup.keyboard[0]) == 1
    assert button.request_location is True


def test_show_map_reply(context):
    context.user_data = utils.get_user_data(Location(-0.09531, 51.521681))
    reply = callbacks.ShowMap().create_reply(context)

    assert reply.location is not None
    assert isinstance(reply.location.latitude, float) is True
    assert isinstance(reply.location.longitude, float) is True

