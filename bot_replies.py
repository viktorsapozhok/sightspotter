# A.Piskun
# 25/11/2018
#
#
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import bot_tools
import config
from constants import STATES


class Reply(object):
    def __init__(self, user_data, callback):
        self.callback = callback
        self.text = ''
        self.markup = None
        self.state = -1
        self.n_sights = 0
        self.next = user_data['next']
        self.n_sights = self.__get_sights_count(user_data['sights'])
        self.sight = self.__get_sight(user_data['sights'], user_data['next'])
        self.history = self.__get_history(user_data['history'], user_data['next'])
        self.__build_reply()

    def __build_reply(self):
        if self.callback == 'start':
            self.__build_start_reply()
        elif self.callback == 'location':
            self.__build_location_reply()
        elif self.callback == 'next':
            self.__build_next_reply()
        elif self.callback == 'answer':
            self.__build_answer_reply()
        elif self.callback == 'history':
            self.__build_history_reply()

    def __build_start_reply(self):
        self.text = bot_tools.get_config_message(config.get('messages').get('start'))
        self.markup = self.__get_current_location_markup()
        self.state = STATES['location']

    def __build_location_reply(self):
        if self.n_sights == 0:
            self.text = self.__get_not_found_reply(config.get('max_distance'))
            self.markup = ReplyKeyboardRemove()
            self.state = STATES['location']
        else:
            self.__build_sight_reply()

    def __build_next_reply(self):
        if self.next > config.get('max_next_events'):
            self.text = config.get('messages').get('max_next_events')
            self.markup = self.__get_current_location_markup()
            self.state = STATES['location']
        elif self.next > self.n_sights:
            self.text = self.__get_next_not_found_reply(config.get('max_distance'))
            self.markup = self.__get_current_location_markup()
            self.state = STATES['location']
        else:
            self.__build_sight_reply()

    def __build_answer_reply(self):
        self.text = self.__get_answer_reply(self.sight)
        self.markup = self.__get_next_markup(self.history)
        self.state = STATES['next']

    def __build_history_reply(self):
        self.text = self.history
        self.markup = self.__get_next_markup(self.history)
        self.state = STATES['next']

    def __build_sight_reply(self):
        self.text = self.__get_sight_reply(self.sight)
        self.markup = self.__get_next_markup(self.history)
        self.state = STATES['next']

    @staticmethod
    def __get_next_markup(history):
        location_button = KeyboardButton(text="send current location", request_location=True)
        if history is None:
            keyboard = [['next', 'answer'], [location_button]]
        else:
            keyboard = [['next', 'answer', 'history'], [location_button]]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)

    @staticmethod
    def __get_current_location_markup():
        keyboard = KeyboardButton(text="send current location", request_location=True)
        return ReplyKeyboardMarkup([[keyboard]], resize_keyboard=True)

    @staticmethod
    def __get_not_found_reply(max_dist):
        reply = config.get('messages').get('not_found')
        reply += ' %.0f км' % max_dist
        return reply

    @staticmethod
    def __get_next_not_found_reply(max_dist):
        msg = config.get('messages').get('next_not_found')
        reply = msg[0]
        reply += ' %.0f км. ' % max_dist
        reply += msg[1]
        return reply

    @staticmethod
    def __get_sight_reply(sight):
        reply = '\n'
        if sight[0] > 1:
            dist_text = '%.0f км' % sight[0]
            reply += '<b>%s</b> (%s)\n' % (sight[1][3], dist_text)
        else:
            reply += '<b>%s</b>\n' % sight[1][3]
        reply += '%s\n<i>%s</i>\n\n' % (sight[1][4], sight[1][5])
        return reply

    @staticmethod
    def __get_answer_reply(sight):
        try:
            reply = sight[1][6]
        except (ValueError, IndexError):
            reply = config.get('messages').get('answer_not_found')
        return reply

    @staticmethod
    def __get_sights_count(sights):
        n_sights = 0
        if sights is not None:
            n_sights = len(sights)
        return n_sights

    @staticmethod
    def __get_sight(sights, next):
        try:
            sight = sights[next]
        except (TypeError, IndexError):
            sight = None
        return sight

    @staticmethod
    def __get_history(histories, next):
        try:
            history = histories[next][0][1]
        except (ValueError, IndexError, TypeError):
            history = None
        return history

