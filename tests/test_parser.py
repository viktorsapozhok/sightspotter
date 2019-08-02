# -*- coding: utf-8 -*-

from sightspotter import config
from sightspotter.parser import RouteParser

commuter = config.get_commuter()


def test_parser():
    parser = RouteParser(commuter, config.parser['url'])
    urls = parser.extract_routes()

    assert len(urls) >= 299

    _urls = [url for url in urls if 'cherepovets2008' in url]
    sights, histories, _, year = parser.parse_route(_urls[0], 0, -1)

    assert len(sights) >= 44
    assert year == 2008

    _urls = [url for url in urls if 'kazan2018' in url]
    sights, histories, _, year = parser.parse_route(_urls[0], 0, -1)

    assert len(sights) >= 37
    assert len(histories) >= 21
    assert year == 2018


def test_sights():
    df = commuter.select('select * from sights')
    assert len(df) > 10000
    assert len(df.columns) == 10


def test_events():
    df = commuter.select('select distinct event from sights')
    assert len(df) >= 218


def test_history():
    df = commuter.select('select * from history')
    assert len(df) > 2500
    assert len(df.columns) == 4


def test_user_log():
    df = commuter.select('select * from user_log')
    assert len(df.columns) == 3


def test_year():
    df = commuter.select('select year from sights where year < 2000')
    assert len(df) == 0

