# -*- coding: utf-8 -*-

"""Bot callbacks
"""

import abc
import logging

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, ConversationHandler

from sightspotter import config
from sightspotter import bot_tools
from sightspotter import replies, utils

logger = logging.getLogger('sightspotter')
commuter = config.get_commuter()


class BotCallback(abc.ABC):
    @abc.abstractmethod
    def update_data(self, update, context):
        raise NotImplementedError

    @abc.abstractmethod
    def create_reply(self, context):
        raise NotImplementedError()

    @abc.abstractmethod
    def create_log(self):
        raise NotImplementedError()

    def callback(self, update, context):
        self.update_data(update, context)
        reply = self.create_reply(context)
        user_log = self.create_log()

        user_name = update.message.from_user.full_name

        update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
        bot_tools.add_user_log(context.user_data['db'], user_name, user_log)

        return reply.state


class Start(BotCallback):
    def update_data(self, update, context):
        context.user_data = bot_tools.init_user_data(context.user_data)

    def create_reply(self, context):
        return replies.StartReply(context.user_data)

    def create_log(self):
        return 'start'


class Location(BotCallback):
    def update_data(self, update, context):
        if not bot_tools.is_initialized(context.user_data):
            context.user_data = bot_tools.init_user_data(context.user_data)
        user_location = update.message.location
        context.user_data = bot_tools.init_new_location(context.user_data, user_location)

    def create_reply(self, context):
        if utils.get_sights_count(context.user_data['sights']) == 0:
            return replies.NotFoundReply(context.user_data)
        else:
            return replies.SightReply(context.user_data)

    def create_log(self):
        return 'location'


def next_sight(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f'{user.full_name}: next')

    context.user_data['next'] += 1
    n_sights = utils.get_sights_count(context.user_data['sights'])

    if context.user_data['next'] > config.n_next:
        reply = replies.MaxNextEventsReply(context.user_data)
    elif context.user_data['next'] >= n_sights:
        reply = replies.NextNotFoundReply(context.user_data)
    else:
        reply = replies.SightReply(context.user_data)

    update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
    bot_tools.add_user_log(context.user_data['db'], user.full_name, 'next')

    return reply.state


def answer(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f'{user.full_name}: answer')

    reply = replies.AnswerReply(context.user_data)

    update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
    bot_tools.add_user_log(context.user_data['db'], user.full_name, 'answer')

    return reply.state


def history(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f'{user.full_name}: history')

    reply = replies.HistoryReply(context.user_data)

    update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
    bot_tools.add_user_log(context.user_data['db'], user.full_name, 'history')

    return reply.state


def show_map(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f'{user.full_name}: map')

    reply = replies.MapReply(context.user_data)

    if reply.location is not None:
        update.message.bot.send_location(
            update.message.chat_id,
            latitude=reply.location.latitude,
            longitude=reply.location.longitude
        )
    else:
        update.message.reply_text(config.messages['unknown'], reply_markup=reply.markup)

    bot_tools.add_user_log(context.user_data['db'], user.full_name, 'show_map')

    return reply.state


def stop(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f'{user.full_name}: stop')
    update.message.reply_text(config.messages['stop'], reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()

    return ConversationHandler.END


def help_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f'{user.full_name}: help')

    update.message.reply_text(config.messages['help'], parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())

    return bot_tools.get_state(context.user_data)


def unknown_command(update: Update, context: CallbackContext):
    update.message.reply_text(config.messages['unknown'])
    return bot_tools.get_state(context.user_data)


def error_message(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

