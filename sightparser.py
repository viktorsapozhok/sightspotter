# A.Piskun
# 28/11/2018
#
# parsing of events from https://www.runcity.org/ru/events/archive/
#
import re
from bs4 import BeautifulSoup
import requests
from dbhelper import DBHelper
import config


class Parser(object):
    def __init__(self, path2db, url, **kwargs):
        self.db = DBHelper(path2db)
        self.url = url
        #if true then overwrite tables, if false then add to tables
        self.parse_all = kwargs.get('parse_all', False)

    def parse(self, logger):
        if self.parse_all:
            self.db.drop_tables()

        self.db.create_tables()

        logger.info('extracting route urls')
        urls = self.extract_route_urls()

        logger.info('parsing routes')
        sights, histories = self.parse_routes(urls, logger)

        if len(sights) > 0:
            logger.info('loading to database')
            self.db.add_sights(sights)
            self.db.add_histories(histories)
        else:
            logger.info('no new routes')

    def extract_route_urls(self):
        soup = BeautifulSoup(requests.get(self.url).content, "html.parser")
        tags = soup.findAll('td', style='width: 100%;')
        urls = ['https:' + tag.find_next()['href'] + 'routes/all/' for tag in tags]
        return urls

    def parse_routes(self, urls, logger):
        sights = []
        histories = []
        index = self.db.get_max_sight_id()
        year = -1

        for url in urls:
            try:
                if self.is_route_parsed(url):
                    break
                else:
                    logger.info('parsing %s', url)
                    sights, histories, index, year = self.parse_route(url, sights, histories, index, year)
            except ValueError:
                continue
        return sights, histories

    def is_route_parsed(self, url):
        event = self.__get_event(url)
        sights = self.db.select_sights_by_event(event)
        if len(sights) == 0:
            return False
        return True

    def parse_route(self, url, sights, histories, index, year_prev):
        event = self.__get_event(url)

        if event is None:
            return sights, histories, index, year_prev

        year = self.__get_year(event, year_prev)
        response = requests.get(url)
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
                    latitude = float(tag.find_next('abbr', class_="latitude").text)
                    longitude = float(tag.find_next('abbr', class_="longitude").text)
                else:
                    continue

                description = self.__get_tag_text(tag, sibling_2, 'description')
                quest = self.__get_tag_text(tag, sibling_3, 'quest')
                answer = self.__get_tag_text(tag, sibling_4, 'answer')
                history = self.__get_tag_history(tag, sibling_5)

                if len(address) < config.get('parser').get('min_length_addr') or \
                   len(description) < config.get('parser').get('min_length_descr') or \
                   len(quest) < config.get('parser').get('min_length_quest') or \
                   len(answer) < config.get('parser').get('min_length_answer'):
                    continue

                if any(word in address.lower() for word in config.get('parser').get('stop_words_addr')) or \
                   any(word in description.lower() for word in config.get('parser').get('stop_words_descr')) or \
                   any(word in quest.lower() for word in config.get('parser').get('stop_words_quest')):
                    continue

            except (ValueError, AttributeError, KeyError):
                continue

            index += 1
            sights.append((index, latitude, longitude, event, cp_id, address, description, quest, answer, year))

            if len(history) > 0:
                histories.append((index, event, cp_id, history))

        return sights, histories, index, year

    @staticmethod
    def __get_event(url):
        try:
            event = url[(url.index('events/') + 7):(url.index('routes/all') - 1)]
        except ValueError:
            event = None
        return event

    @staticmethod
    def __get_year(event, year_prev):
        try:
            year = int(event[-4:])
        except ValueError:
            year = year_prev
        return year

    @staticmethod
    def __get_tag_text(tag, sibling, attr):
        if attr not in sibling.attrs['class']:
            text = ''
        else:
            text = tag.find_next('dd', class_=attr).text.lstrip().rstrip()
            #replace multiple spaces by single space
            text = ' '.join(text.split())
            #remove dot in the end of text
            if len(text) > 0:
                if text[-1] == '.':
                    text = text[:-1]
        return text

    @staticmethod
    def __get_tag_history(tag, sibling):
        history = ''
        try:
            if 'class' in sibling.attrs:
                if 'history' in sibling.attrs['class']:
                    history = tag.find_next('dd', class_='history').text.lstrip().rstrip()
                    history = ' '.join(history.split())
                    for word in config.get('parser').get('remove_words_hist'):
                        history = history.replace(word, '').lstrip().rstrip()
        except (ValueError, AttributeError, KeyError):
            history = ''
        return history


