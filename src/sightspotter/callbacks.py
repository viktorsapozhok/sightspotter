# -*- coding: utf-8 -*-

"""Bot callbacks
"""

import logging

from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from sightspotter import config
from sightspotter import bot_tools
from sightspotter import replies
from sightspotter import utils

logger = logging.getLogger('sightspotter')


def start(bot, update, user_data):
    user = update.message.from_user
    logger.info(f'{user.full_name}: start')

    user_data = bot_tools.init_user_data(user_data)
    reply = replies.StartReply(user_data)

    update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
    bot_tools.add_user_log(user_data['db'], user.full_name, 'start')

    return reply.state


def location(bot, update, user_data):
    user = update.message.from_user
    user_location = update.message.location
    logger.info(f'{user.full_name}: location')

    if not bot_tools.is_initialized(user_data):
        user_data = bot_tools.init_user_data(user_data)

    user_data = bot_tools.init_new_location(user_data, user_location)

    if utils.get_sights_count(user_data['sights']) == 0:
        reply = replies.NotFoundReply(user_data)
    else:
        reply = replies.SightReply(user_data)

    update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
    bot_tools.add_user_log(user_data['db'], user.full_name, 'location')

    return reply.state


def next_sight(bot, update, user_data):
    user = update.message.from_user
    logger.info(f'{user.full_name}: next')

    user_data['next'] += 1
    n_sights = utils.get_sights_count(user_data['sights'])

    if user_data['next'] > config.n_next:
        reply = replies.MaxNextEventsReply(user_data)
    elif user_data['next'] >= n_sights:
        reply = replies.NextNotFoundReply(user_data)
    else:
        reply = replies.SightReply(user_data)

    update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
    bot_tools.add_user_log(user_data['db'], user.full_name, 'next')

    return reply.state


def answer(bot, update, user_data):
    user = update.message.from_user
    logger.info(f'{user.full_name}: answer')

    reply = replies.AnswerReply(user_data)

    update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
    bot_tools.add_user_log(user_data['db'], user.full_name, 'answer')

    return reply.state


def history(bot, update, user_data):
    user = update.message.from_user
    logger.info(f'{user.full_name}: history')

    reply = replies.HistoryReply(user_data)

    update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
    bot_tools.add_user_log(user_data['db'], user.full_name, 'history')

    return reply.state


def show_map(bot, update, user_data):
    user = update.message.from_user
    logger.info(f'{user.full_name}: map')

    reply = replies.MapReply(user_data)

    if reply.location is not None:
        bot.sendLocation(
            update.message.chat_id,
            latitude=reply.location.latitude,
            longitude=reply.location.longitude)
    else:
        update.message.reply_text(config.messages['unknown'], reply_markup=reply.markup)

    bot_tools.add_user_log(user_data['db'], user.full_name, 'show_map')

    return reply.state


def stop(bot, update, user_data):
    user = update.message.from_user
    logger.info(f'{user.full_name}: stop')
    update.message.reply_text(config.messages['stop'], reply_markup=ReplyKeyboardRemove())
    user_data.clear()

    return ConversationHandler.END


def help_message(bot, update, user_data):
    user = update.message.from_user
    logger.info(f'{user.full_name}: help')

    update.message.reply_text(config.messages['help'], parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())

    return bot_tools.get_state(user_data)


def unknown_command(bot, update, user_data):
    update.message.reply_text(config.messages['unknown'])
    return bot_tools.get_state(user_data)


def error_message(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

