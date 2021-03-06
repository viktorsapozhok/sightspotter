# -*- coding: utf-8 -*-

"""Parse routes from https://www.runcity.org.
"""
__all__ = ['RouteParser']

import logging
import re
from typing import Any, List

from bs4 import BeautifulSoup
import pandas as pd
import requests
from tqdm import tqdm

from . import config

logger = logging.getLogger('sightspotter')


class RouteParser(object):
    """Parse routes.

    Parse routes, addresses, tasks and histories
    from https://www.runcity.org.

    Collected data is placed to sqlite database.

    Args:
        commuter:
            Database communication agent.
        url:
            Base URL.
    """

    def __init__(self, commuter, url):
        self.commuter = commuter
        self.base_url = url

    def parse(self):
        logger.info('extracting routes')
        routes = self.extract_routes()
        self.parse_routes(routes)

    def extract_routes(self):
        """Extract events and make route URL's.
        """

        soup = BeautifulSoup(requests.get(self.base_url).content, "html.parser")
        tags = soup.findAll('td', style='width: 100%;')
        urls = ['https:' + tag.find_next()['href'] + 'routes/all/'
                for tag in tags]
        return urls

    def parse_routes(self, routes):
        sights = []
        histories = []
        sight_id = self._get_max_index()
        year = -1

        for route in tqdm(routes, desc='parsing routes', ascii=True):
            try:
                if self._is_route_parsed(route):
                    continue
                else:
                    # parse sights and histories from route page
                    sights, histories, sight_id, year = \
                        self.parse_route(route, sight_id, year)
                    event = self._get_event(route)

                    # export parsed data to database
                    self._insert_to_table('routes', [[event, year, route]])
                    self._insert_to_table('sights', sights)
                    self._insert_to_table('history', histories)
            except ValueError:
                continue

        return sights, histories

    def parse_route(self, route, index, year_prev):
        event = self._get_event(route)

        if event is None:
            return [], [], index, year_prev

        sights = []  # type: List[List[Any]]
        histories = []  # type: List[List[Any]]
        year = self._get_year(event, year_prev)
        response = requests.get(route)
        soup = BeautifulSoup(response.content, "html.parser")
        tags = soup.findAll(id=re.compile("cp"))

        for tag in tags:
            try:
                cp_id = tag['id']
                address = tag.text.rstrip().lstrip()
                address = address[5:].lstrip()

                sibling_1 = tag.find_next_sibling()
                sibling_2 = sibling_1.find_next_sibling()
                sibling_3 = sibling_2.find_next_sibling()
                sibling_4 = sibling_3.find_next_sibling()
                sibling_5 = sibling_4.find_next_sibling()

                if 'geo' in sibling_1.attrs['class']:
                    latitude = float(
                        tag.find_next('abbr', class_="latitude").text)
                    longitude = float(
                        tag.find_next('abbr', class_="longitude").text)
                else:
                    continue

                description = \
                    self._get_tag_text(tag, sibling_2, 'description')
                quest = self._get_tag_text(tag, sibling_3, 'quest')
                answer = self._get_tag_text(tag, sibling_4, 'answer')
                history = self._get_tag_history(tag, sibling_5)

                if (len(address) < config.parser['min_length_addr'] or
                    len(description) < config.parser['min_length_descr'] or
                    len(quest) < config.parser['min_length_quest'] or
                    len(answer) < config.parser['min_length_answer']):  # noqa: E129
                    continue

                if (any(word in address.lower()
                        for word in config.parser['stop_words_addr']) or
                    any(word in description.lower()
                        for word in config.parser['stop_words_descr']) or
                    any(word in quest.lower()
                        for word in config.parser['stop_words_quest'])):
                    continue

            except (ValueError, AttributeError, KeyError):
                continue

            index += 1
            sights += [[index, latitude, longitude, event, cp_id,
                        address, description, quest, answer, year]]

            if len(history) > 0:
                histories += [[index, event, cp_id, history]]

        return sights, histories, index, year

    def _insert_to_table(self, table_name, lol):
        if len(lol) > 0:
            df = pd.DataFrame.from_records(lol)
            df.columns = config.db_config[table_name]
            self.commuter.insert(table_name, df)

    def _is_route_parsed(self, route):
        event = self._get_event(route)
        sights = self._get_event_sights(event)
        return len(sights) > 0

    def _get_event_sights(self, event):
        sql = f'SELECT sight_id FROM sights WHERE event=\'{event}\''

        return self.commuter.select(sql)

    def _get_max_index(self):
        cmd = 'SELECT MAX(sight_id) FROM sights'
        return self.commuter.select(cmd=cmd, return_scalar=0)

    @staticmethod
    def _get_event(route):
        try:
            index_1 = route.index('events/') + 7
            index_2 = route.index('routes/all') - 1
            event = route[index_1:index_2]
        except ValueError:
            event = None
        return event

    @staticmethod
    def _get_year(event, year_prev):
        try:
            year = int(event[-4:])
        except ValueError:
            year = year_prev
        return year

    @staticmethod
    def _get_tag_text(tag, sibling, attr):
        if attr not in sibling.attrs['class']:
            text = ''
        else:
            text = tag.find_next('dd', class_=attr).text.lstrip().rstrip()
            # replace multiple spaces by single space
            text = ' '.join(text.split())
            # remove dot in the end of text
            if len(text) > 0:
                if text[-1] == '.':
                    text = text[:-1]
        return text

    @staticmethod
    def _get_tag_history(tag, sibling):
        history = ''

        try:
            if 'class' in sibling.attrs:
                if 'history' in sibling.attrs['class']:
                    history = tag.find_next(
                        'dd', class_='history').text.lstrip().rstrip()
                    history = ' '.join(history.split())
                    for word in config.parser['remove_words_hist']:
                        history = history.replace(word, '').lstrip().rstrip()
        except (ValueError, AttributeError, KeyError):
            history = ''

        return history
