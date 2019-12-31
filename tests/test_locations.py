# -*- coding: utf-8 -*-
from telegram import Location

from bot import config, utils


def test_remote_location():
    sights, _ = utils.get_sights(Location(20.4, 57.9))
    assert len(sights) == 0


def test_sight_location():
    sights, _ = utils.get_sights(Location(37.620948, 55.688832))
    assert sights[0][1] == 55.688832
    assert sights[0][2] == 37.620948


def test_sight_history():
    _, history = utils.get_sights(Location(-0.09531, 51.521681))
    _history = history[0][0][1][:25]

    assert len(history[0][0][1]) > 1000
    for word in config.parser['remove_words_hist']:
        assert word not in _history.lower()
