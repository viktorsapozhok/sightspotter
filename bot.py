# A.Piskun
# 05/11/2018
#
#
import argparse
import logging
import os
import re
from telegram import ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import config
from sightparser import Parser
import bot_tools
from bot_replies import Reply
from constants import PATHS, STATES

config.init_from_json(PATHS['to_config'])
logging.basicConfig(format=config.get('logging').get('format'),
                    level=logging.INFO, datefmt=config.get('logging').get('date_fmt'))
logger = logging.getLogger(__name__)


def start(bot, update, user_data):
    user = update.message.from_user
    logger.info("User %s started the conversation", user.first_name)
    user_data = bot_tools.init_user_data(user_data)
    reply = Reply(user_data, 'start')
    update.message.reply_text(reply.text, reply_markup=reply.markup)
    bot_tools.add_user_log(user_data['db'], user.full_name, 'start')
    return reply.state


def location(bot, update, user_data):
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Location of %s: %f / %f", user.first_name,
                user_location.latitude, user_location.longitude)

    if not bot_tools.is_initialized(user_data):
        user_data = bot_tools.init_user_data(user_data)

    user_data = bot_tools.init_new_location(user_data, user_location)
    reply = Reply(user_data, 'location')
    update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
    bot_tools.add_user_log(user_data['db'], user.full_name, 'location')
    return reply.state


def bot_next(bot, update, user_data):
    user = update.message.from_user
    logger.info("%s: %s", user.first_name, update.message.text)
    user_data['next'] += 1
    reply = Reply(user_data, 'next')
    update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
    bot_tools.add_user_log(user_data['db'], user.full_name, 'next')
    return reply.state


def answer(bot, update, user_data):
    user = update.message.from_user
    logger.info("%s: %s", user.first_name, update.message.text)
    reply = Reply(user_data, 'answer')
    update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
    bot_tools.add_user_log(user_data['db'], user.full_name, 'answer')
    return reply.state


def history(bot, update, user_data):
    user = update.message.from_user
    logger.info("%s: %s", user.first_name, update.message.text)
    reply = Reply(user_data, 'history')
    update.message.reply_text(reply.text, parse_mode='Markdown', reply_markup=reply.markup)
    bot_tools.add_user_log(user_data['db'], user.full_name, 'history')
    return reply.state


def show_map(bot, update, user_data):
    user = update.message.from_user
    logger.info("%s: %s", user.first_name, update.message.text)
    reply = Reply(user_data, 'show_map')

    if reply.location is not None:
        bot.sendLocation(update.message.chat_id,
                         latitude=reply.location.latitude,
                         longitude=reply.location.longitude)
    else:
        update.message.reply_text(config.get('messages').get('unknown'), reply_markup=reply.markup)

    bot_tools.add_user_log(user_data['db'], user.full_name, 'show_map')
    return reply.state


def stop(bot, update, user_data):
    user = update.message.from_user
    logger.info("User %s stopped the conversation", user.first_name)
    update.message.reply_text(config.get('messages').get('stop'), reply_markup=ReplyKeyboardRemove())
    user_data.clear()
    return ConversationHandler.END


def bot_help(bot, update, user_data):
    user = update.message.from_user
    logger.info("User %s opened help", user.first_name)
    update.message.reply_text(
        bot_tools.get_config_message(config.get('messages').get('help')),
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return bot_tools.get_state(user_data)


def unknown_command(bot, update, user_data):
    update.message.reply_text(config.get('messages').get('unknown'))
    return bot_tools.get_state(user_data)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-test', action='store_true')
    args = parser.parse_args()

    if args.test:
        logger.info('running test bot')
        token = os.environ['SSB_TEST_TOKEN']
    else:
        token = os.environ['SSB_TOKEN']

    #check new routes and parse if exists
    parser = Parser(PATHS['to_db'], config.get('parser').get('url'))
    parser.parse(logger)

    updater = Updater(token)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True),
                      MessageHandler(Filters.location, location, pass_user_data=True)],
        states={
            STATES['location']: [MessageHandler(Filters.location, location, pass_user_data=True)],
            STATES['next']: [MessageHandler(Filters.location, location, pass_user_data=True),
                   MessageHandler(Filters.regex(re.compile('^(next)$', re.I)), bot_next, pass_user_data=True),
                   MessageHandler(Filters.regex(re.compile('^(answer)$', re.I)), answer, pass_user_data=True),
                   MessageHandler(Filters.regex(re.compile('^(history)$', re.I)), history, pass_user_data=True),
                   MessageHandler(Filters.regex(re.compile('^(show map)$', re.I)), show_map, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('stop', stop, pass_user_data=True)],
        conversation_timeout=config.get('timeout_in_sec')
    )
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('help', bot_help, pass_user_data=True))
    dp.add_handler(CommandHandler('start', start, pass_user_data=True))
    dp.add_handler(CommandHandler('stop', stop, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.command, unknown_command, pass_user_data=True))
    dp.add_handler(MessageHandler('', unknown_command, pass_user_data=True))
    dp.add_error_handler(error)
    logger.info("started polling")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

