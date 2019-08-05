# -*- coding: utf-8 -*-

"""Bot callbacks
"""

import abc
import logging

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, ConversationHandler

from sightspotter import config
from sightspotter import replies, utils

logger = logging.getLogger('sightspotter')


class BotCallback(abc.ABC):
    def callback(self, update, context):
        self.update_data(update, context)
        reply = self.create_reply(context)

        user_name = update.message.from_user.full_name

        update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
        utils.write_log(user_name, self.__class__.__name__)

        return reply.state

    @abc.abstractmethod
    def create_reply(self, context):
        raise NotImplementedError()

    def update_data(self, update, context):
        pass


class Start(BotCallback):
    def update_data(self, update, context):
        context.user_data.update(utils.get_user_data())

    def create_reply(self, context):
        return replies.StartReply(context.user_data)


class Location(BotCallback):
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


class NextSight(BotCallback):
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


class Answer(BotCallback):
    def create_reply(self, context):
        return replies.AnswerReply(context.user_data)


class History(BotCallback):
    def create_reply(self, context):
        return replies.HistoryReply(context.user_data)


class ShowMap(BotCallback):
    def create_reply(self, context):
        return replies.MapReply(context.user_data)

    def callback(self, update, context):
        reply = self.create_reply(context)

        user_name = update.message.from_user.full_name

        if reply.location is not None:
            update.message.bot.send_location(
                update.message.chat_id,
                latitude=reply.location.latitude,
                longitude=reply.location.longitude
            )
        else:
            update.message.reply_text(config.messages['unknown'], reply_markup=reply.markup)

        utils.write_log(user_name, self.__class__.__name__)

        return reply.state


def stop_callback(update: Update, context: CallbackContext):
    update.message.reply_text(
        config.messages['stop'],
        reply_markup=ReplyKeyboardRemove()
    )

    logger.info(f'{update.message.from_user.full_name}: stop')
    context.user_data.clear()

    return ConversationHandler.END


def help_callback(update: Update, context: CallbackContext):
    update.message.reply_text(
        config.messages['help'],
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )

    logger.info(f'{update.message.from_user.full_name}: help')
    return utils.get_state(context.user_data)


def unknown_callback(update: Update, context: CallbackContext):
    update.message.reply_text(config.messages['unknown'])
    return utils.get_state(context.user_data)


def error_callback(update, context):
    logger.warning(f'Update {update} caused error {context.error}')

