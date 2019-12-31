# -*- coding: utf-8 -*-

"""Bot replies
"""
__all__ = [
    'StartReply',
    'NotFoundReply',
    'SightReply',
    'MaxNextEventsReply',
    'NextNotFoundReply',
    'AnswerReply',
    'HistoryReply',
    'MapReply'
]

import abc

from telegram import (
    KeyboardButton,
    Location,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)

from . import config


class BaseReply(abc.ABC):
    def __init__(self, user_data):
        self.user_data = user_data

    @property
    @abc.abstractmethod
    def text(self):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def markup(self):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def state(self):
        raise NotImplementedError()


class StartReply(BaseReply):
    def __init__(self, user_data):
        super().__init__(user_data)

    @property
    def text(self):
        return config.messages['start']

    @property
    def markup(self):
        keyboard = KeyboardButton(
            config.button_titles['location'],
            request_location=True
        )
        return ReplyKeyboardMarkup([[keyboard]], resize_keyboard=True)

    @property
    def state(self):
        return config.states['location']


class NotFoundReply(BaseReply):
    def __init__(self, user_data):
        super().__init__(user_data)

    @property
    def text(self):
        return config.messages['not_found']

    @property
    def markup(self):
        return ReplyKeyboardRemove()

    @property
    def state(self):
        return config.states['location']


class SightReply(BaseReply):
    def __init__(self, user_data):
        super().__init__(user_data)

        self.sight = self._get_sight()
        self.history = self._get_history()

    @property
    def text(self):
        nl = '\n'
        reply = \
            f'*Адрес:*{nl + str(self.sight[3]) + nl + nl} ' \
            f'*Задание:*{nl + str(self.sight[4])}. ' \
            f'{str(self.sight[5]) + nl + nl} ' \
            f'*Год маршрута:*{nl + str(self.sight[7])}'
        return reply

    @property
    def markup(self):
        location_button = KeyboardButton(
            text=config.button_titles['location'],
            request_location=True
        )

        if self.history is None:
            keyboard = [
                [config.button_titles['next'],
                 config.button_titles['answer']],
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

    @property
    def state(self):
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


class MaxNextEventsReply(StartReply):
    def __init__(self, user_data):
        super().__init__(user_data)

    @property
    def text(self):
        return config.messages['max_next_events']


class NextNotFoundReply(StartReply):
    def __init__(self, user_data):
        super().__init__(user_data)

    @property
    def text(self):
        return config.messages['next_not_found']


class AnswerReply(SightReply):
    def __init__(self, user_data):
        super().__init__(user_data)

    @property
    def text(self):
        try:
            reply = self.sight[6]
        except (ValueError, IndexError):
            reply = config.messages['answer_not_found']
        return reply


class HistoryReply(SightReply):
    def __init__(self, user_data):
        super().__init__(user_data)

    @property
    def text(self):
        return self.history


class MapReply(SightReply):
    def __init__(self, user_data):
        super().__init__(user_data)

    @property
    def location(self):
        return Location(self.sight[2], self.sight[1])
