# -*- coding: utf-8 -*-

"""Bot callbacks
"""
__all__ = [
    'Start',
    'Location',
    'NextSight',
    'Answer',
    'History',
    'ShowMap',
    'stop',
    'info',
    'unknown',
    'error',
]

import abc
import logging

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, ConversationHandler

from . import config, replies, utils

logger = logging.getLogger('sightspotter')


class BaseCallback(abc.ABC):
    """Base class for callbacks.

    Calling class instance updates user data, generates reply text
    and writes log to database.
    """

    def __call__(self, update, context):
        self.update_data(update, context)
        reply = self.create_reply(context)

        user_name = update.message.from_user.full_name

        # generate reply
        update.message.reply_text(
            reply.text,
            parse_mode='Markdown',
            reply_markup=reply.markup)

        # write log to db
        utils.write_log(
            user_name=user_name,
            user_log=self.__class__.__name__)

        return reply.state

    @abc.abstractmethod
    def create_reply(self, context):
        """Generate reply text.
        """

        raise NotImplementedError()

    def update_data(self, update, context):
        """Update user data.
        """

        pass


class Start(BaseCallback):
    """Activated on pushing the start button.
    """

    def update_data(self, update, context):
        context.user_data.update(utils.get_user_data())

    def create_reply(self, context):
        return replies.StartReply(context.user_data)


class Location(BaseCallback):
    """Activated when user sent a location.

    User current location is caching via `context`.
    Reply contains the nearest found sight.
    """

    def update_data(self, update, context):
        if not utils.is_user_data_initialized(context.user_data):
            context.user_data.update(utils.get_user_data())

        user_location = update.message.location
        context.user_data.update(utils.get_user_data(user_location))

    def create_reply(self, context):
        if utils.get_sights_count(context.user_data['sights']) == 0:
            return replies.NotFoundReply(context.user_data)
        else:
            return replies.SightReply(context.user_data)


class NextSight(BaseCallback):
    """Activated on `next` button event.

    Reply contains the next nearest sight.
    """

    def update_data(self, update, context):
        context.user_data['next'] += 1

    def create_reply(self, context):
        n_sights = utils.get_sights_count(context.user_data['sights'])

        if context.user_data['next'] > config.n_next:
            return replies.MaxNextEventsReply(context.user_data)
        elif context.user_data['next'] >= n_sights:
            return replies.NextNotFoundReply(context.user_data)
        else:
            return replies.SightReply(context.user_data)


class Answer(BaseCallback):
    """Show answer.
    """

    def create_reply(self, context):
        return replies.AnswerReply(context.user_data)


class History(BaseCallback):
    """Show history if exists.
    """

    def create_reply(self, context):
        return replies.HistoryReply(context.user_data)


class ShowMap(BaseCallback):
    """Show map with the address of the current sight.
    """

    def __call__(self, update, context):
        reply = self.create_reply(context)

        user_name = update.message.from_user.full_name

        if reply.location is not None:
            update.message.bot.send_location(
                update.message.chat_id,
                latitude=reply.location.latitude,
                longitude=reply.location.longitude)
        else:
            update.message.reply_text(
                config.messages['unknown'],
                reply_markup=reply.markup)

        utils.write_log(
            user_name=user_name,
            user_log=self.__class__.__name__)

        return reply.state

    def create_reply(self, context):
        return replies.MapReply(context.user_data)


def stop(update, context):
    """Stop conversation and remove user_data.
    """

    update.message.reply_text(
        config.messages['stop'],
        reply_markup=ReplyKeyboardRemove())

    logger.info(f'{update.message.from_user.full_name}: stop')

    # clear cache
    context.user_data.clear()

    return ConversationHandler.END


def info(update, context):
    """Show help information.
    """

    update.message.reply_text(
        config.messages['help'],
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove())

    logger.info(f'{update.message.from_user.full_name}: help')
    return utils.get_state(context.user_data)


def unknown(update: Update, context: CallbackContext):
    """Activated when user command is not recognized.
    """

    update.message.reply_text(config.messages['unknown'])
    return utils.get_state(context.user_data)


def error(update, context):
    """Activated if error occurred.
    """

    logger.warning(f'Update {update} caused error {context.error}')
