
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Location
from sightspotter import bot_tools
from sightspotter import config


class Reply(object):
    def __init__(self, user_data, callback):
        self.callback = callback
        self.text = ''
        self.markup = None
        self.state = -1
        self.location = None
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
        elif self.callback == 'show_map':
            self.__build_show_map_reply()

    def __build_start_reply(self):
        self.text = config.messages['start']
        self.markup = self.__get_current_location_markup()
        self.state = config.states['location']

    def __build_location_reply(self):
        if self.n_sights == 0:
            self.text = self.__get_not_found_reply(config.max_dist)
            self.markup = ReplyKeyboardRemove()
            self.state = config.states['location']
        else:
            self.__build_sight_reply()

    def __build_next_reply(self):
        if self.next > config.n_next:
            self.text = config.messages['max_next_events']
            self.markup = self.__get_current_location_markup()
            self.state = config.states['location']
        elif self.next >= self.n_sights:
            self.text = self.__get_next_not_found_reply(config.max_dist)
            self.markup = self.__get_current_location_markup()
            self.state = config.states['location']
        else:
            self.__build_sight_reply()

    def __build_answer_reply(self):
        self.text = self.__get_answer_reply(self.sight)
        self.markup = self.__get_next_markup(self.history)
        self.state = config.states['next']

    def __build_history_reply(self):
        self.text = self.history
        self.markup = self.__get_next_markup(self.history)
        self.state = config.states['next']

    def __build_show_map_reply(self):
        self.location = Location(self.sight[2], self.sight[1])
        self.markup = self.__get_next_markup(self.history)
        self.state = config.states['next']

    def __build_sight_reply(self):
        self.text = self.__get_sight_reply(self.sight)
        self.markup = self.__get_next_markup(self.history)
        self.state = config.states['next']

    @staticmethod
    def __get_next_markup(history):
        location_button = KeyboardButton(
            text=config.button_titles['location'], request_location=True)
        if history is None:
            keyboard = [
                [config.button_titles['next'], config.button_titles['answer']],
                [config.button_titles['map']], [location_button]]
        else:
            keyboard = [[config.button_titles['next'],
                         config.button_titles['answer'],
                         config.button_titles['history']],
                        [config.button_titles['map']], [location_button]]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)

    @staticmethod
    def __get_current_location_markup():
        keyboard = KeyboardButton(
            config.button_titles['location'], request_location=True)
        return ReplyKeyboardMarkup([[keyboard]], resize_keyboard=True)

    @staticmethod
    def __get_not_found_reply(max_dist):
        reply = config.messages['not_found']
        reply += ' %.0f км' % max_dist
        return reply

    @staticmethod
    def __get_next_not_found_reply(max_dist):
        msg = config.messages['next_not_found']
        reply = msg[0]
        reply += ' %.0f км. ' % max_dist
        reply += msg[1]
        return reply

    @staticmethod
    def __get_sight_reply(sight):
        reply = '*Адрес:*\n%s\n\n' % sight[3]
        reply += '*Задание:*\n%s. %s\n\n' % (sight[4], sight[5])
        reply += '*Год маршрута:*\n%s' % sight[7]
        return reply

    @staticmethod
    def __get_answer_reply(sight):
        try:
            reply = sight[6]
        except (ValueError, IndexError):
            reply = config.messages['answer_not_found']
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

