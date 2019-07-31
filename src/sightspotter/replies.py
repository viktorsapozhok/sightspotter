# -*- coding: utf-8 -*-

"""Bot replies
"""

import abc

from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import KeyboardButton
from telegram import Location

from sightspotter import config
from sightspotter import utils


class BotReply(abc.ABC):
    def __init__(self, user_data):
        self.user_data = user_data

        self.text = self.get_text()
        self.markup = self.get_markup()
        self.state = self.get_state()

    @abc.abstractmethod
    def get_text(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_markup(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_state(self):
        raise NotImplementedError()


class StartReply(BotReply):
    def __init__(self, user_data):
        super().__init__(user_data)

    def get_text(self):
        return config.messages['start']

    def get_markup(self):
        keyboard = KeyboardButton(
            config.button_titles['location'],
            request_location=True
        )
        return ReplyKeyboardMarkup([[keyboard]], resize_keyboard=True)

    def get_state(self):
        return config.states['location']


class NotFoundReply(BotReply):
    def __init__(self, user_data):
        super().__init__(user_data)

    def get_text(self):
        return config.messages['not_found']

    def get_markup(self):
        return ReplyKeyboardRemove()

    def get_state(self):
        return config.states['location']


class SightReply(BotReply):
    def __init__(self, user_data):
        super().__init__(user_data)

        self.sight = self._get_sight()
        self.history = self._get_history()

    def get_text(self):
        nl = '\n'
        reply = \
            f'*Адрес:*{nl + self.sight[3] + nl + nl} ' \
            f'*Задание:*{nl + self.sight[4]}. {self.sight[5] + nl + nl} ' \
            f'*Год маршрута:*{nl + self.sight[7]}'
        return reply

    def get_markup(self):
        location_button = KeyboardButton(
            text=config.button_titles['location'],
            request_location=True
        )

        if self.history is None:
            keyboard = [
                [config.button_titles['next'], config.button_titles['answer']],
                [config.button_titles['map']], [location_button]]
        else:
            keyboard = [[config.button_titles['next'],
                         config.button_titles['answer'],
                         config.button_titles['history']],
                        [config.button_titles['map']], [location_button]]

        return ReplyKeyboardMarkup(
            keyboard,
            one_time_keyboard=False,
            resize_keyboard=True)

    def get_state(self):
        return config.states['next']

    def _get_sight(self):
        try:
            _sights = self.user_data['sights']
            _next = self.user_data['next']
            sight = _sights[_next]
        except (TypeError, IndexError):
            sight = None
        return sight

    def _get_history(self):
        try:
            _history = self.user_data['history']
            _next = self.user_data['next']
            history = _history[_next][0][1]
        except (ValueError, IndexError, TypeError):
            history = None
        return history


class LocationReply(NotFoundReply, SightReply):
    def __init__(self, user_data):
        if utils.get_sights_count(user_data['sights']) == 0:
            super(NotFoundReply, self).__init__(user_data)
        else:
            super(SightReply, self).__init__(user_data)


class MaxNextEventsReply(StartReply):
    def __init__(self, user_data):
        super().__init__(user_data)

    def get_text(self):
        return config.messages['max_next_events']


class NextNotFoundReply(StartReply):
    def __init__(self, user_data):
        super().__init__(user_data)

    def get_text(self):
        return config.messages['next_not_found']


class NextReply(MaxNextEventsReply, NextNotFoundReply, SightReply):
    def __init__(self, user_data):
        n_sights = utils.get_sights_count(user_data['sights'])

        if user_data['next'] > config.n_next:
            super(MaxNextEventsReply, self).__init__(user_data)
        elif user_data['next'] >= n_sights:
            super(NextNotFoundReply, self).__init__(user_data)
        else:
            super(SightReply, self).__init__(user_data)


class AnswerReply(SightReply):
    def __init__(self, user_data):
        super().__init__(user_data)

    def get_text(self):
        try:
            reply = self.sight[6]
        except (ValueError, IndexError):
            reply = config.messages['answer_not_found']
        return reply


class HistoryReply(SightReply):
    def __init__(self, user_data):
        super().__init__(user_data)

    def get_text(self):
        return self.history


class MapReply(SightReply):
    def __init__(self, user_data):
        super().__init__(user_data)
        self.location = Location(self.sight[2], self.sight[1])
