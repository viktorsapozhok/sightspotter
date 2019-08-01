# -*- coding: utf-8 -*-

"""Bot callbacks
"""

import logging

from telegram import Bot
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import ConversationHandler
from telegram.ext import CallbackContext

from sightspotter import config
from sightspotter import bot_tools
from sightspotter import replies
from sightspotter import utils

logger = logging.getLogger('sightspotter')


def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f'{user.full_name}: start')

    context.user_data = bot_tools.init_user_data(context.user_data)
    reply = replies.StartReply(context.user_data)

    update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
    bot_tools.add_user_log(context.user_data['db'], user.full_name, 'start')

    return reply.state


def location(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_location = update.message.location
    logger.info(f'{user.full_name}: location')

    if not bot_tools.is_initialized(context.user_data):
        context.user_data = bot_tools.init_user_data(context.user_data)

    context.user_data = bot_tools.init_new_location(context.user_data, user_location)

    if utils.get_sights_count(context.user_data['sights']) == 0:
        reply = replies.NotFoundReply(context.user_data)
    else:
        reply = replies.SightReply(context.user_data)

    update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
    bot_tools.add_user_log(context.user_data['db'], user.full_name, 'location')

    return reply.state


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


def show_map(bot: Bot, update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f'{user.full_name}: map')

    reply = replies.MapReply(context.user_data)

    if reply.location is not None:
        bot.sendLocation(
            update.message.chat_id,
            latitude=reply.location.latitude,
            longitude=reply.location.longitude)
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

