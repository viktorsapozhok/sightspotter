# A.Piskun
# 28/11/2018
#
#
import sqlite3
from sightparser import Parser
import config
from constants import PATHS


def test_parser():
    parser = Parser(PATHS['to_db'], config.get('parser').get('url'))
    urls = parser.extract_route_urls()
    assert len(urls) >= 299

    url = [u for u in urls if 'cherepovets2008' in u]
    sights, histories, _, year = parser.parse_route(url[0], [], [], 0, -1)
    assert len(sights) >= 44
    assert year == 2008

    url = [u for u in urls if 'kazan2018' in u]
    sights, histories, _, year = parser.parse_route(url[0], [], [], 0, -1)
    assert len(sights) >= 37
    assert len(histories) >= 21
    assert year == 2018


def test_tables():
    conn = sqlite3.connect(PATHS['to_db'])
    cur = conn.cursor()
    cur.execute('SELECT * FROM sights')
    t = cur.fetchall()
    assert len(t) > 10000
    assert len(t[0]) == 10

    cur.execute('SELECT DISTINCT event FROM sights')
    t = cur.fetchall()
    assert len(t) >= 218

    cur.execute('SELECT * FROM history')
    t = cur.fetchall()
    assert len(t) > 2500
    assert len(t[0]) == 4

    cur.execute('SELECT * FROM user_log')
    t = cur.fetchall()
    assert len(t[0]) == 3


def test_sights_year():
    conn = sqlite3.connect(PATHS['to_db'])
    cur = conn.cursor()
    cur.execute('SELECT year FROM sights where year < 2000')
    t = cur.fetchall()
    assert len(t) == 0

