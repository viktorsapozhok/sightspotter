# -*- coding: utf-8 -*-

"""Command line interface
"""

import click
import os

from telegram.ext import CommandHandler, ConversationHandler
from telegram.ext import Filters, MessageHandler, Updater

from sightspotter.parser import RouteParser
from sightspotter import callbacks, config, utils

logger = config.setup_logger()


@click.group()
def sightspotter():
    """Telegram bot for discovering hidden city gems
    """


#@sightspotter.command()
#@click.option(
#    '--test', is_flag=True, help='Running in test environment')
def poll(test):
    """Start polling
    """
    token = config.test_token if test else config.token

    # commands
    cmd_next = utils.command_pattern(config.button_titles['next'])
    cmd_answer = utils.command_pattern(config.button_titles['answer'])
    cmd_history = utils.command_pattern(config.button_titles['history'])
    cmd_map = utils.command_pattern(config.button_titles['map'])

    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    entry_points = [
        CommandHandler('start', callbacks.Start().callback, pass_user_data=True),
        MessageHandler(Filters.location, callbacks.Location().callback, pass_user_data=True)
    ]

    conversation_states = {
        config.states['location']: [
            MessageHandler(Filters.location, callbacks.Location().callback, pass_user_data=True)
        ],
        config.states['next']: [
            MessageHandler(Filters.location, callbacks.Location().callback, pass_user_data=True),
            MessageHandler(Filters.regex(cmd_next), callbacks.next_sight, pass_user_data=True),
            MessageHandler(Filters.regex(cmd_answer), callbacks.answer, pass_user_data=True),
            MessageHandler(Filters.regex(cmd_history), callbacks.history, pass_user_data=True),
            MessageHandler(Filters.regex(cmd_map), callbacks.show_map, pass_user_data=True)
        ]
    }

    fallbacks = [CommandHandler('stop', callbacks.stop, pass_user_data=True)]

    conversation_handler = ConversationHandler(
        entry_points=entry_points,
        states=conversation_states,
        fallbacks=fallbacks
    )

    dispatcher.add_handler(conversation_handler)
    dispatcher.add_handler(CommandHandler('help', callbacks.help_message, pass_user_data=True))
    dispatcher.add_handler(CommandHandler('start', callbacks.Start().callback, pass_user_data=True))
    dispatcher.add_handler(CommandHandler('stop', callbacks.stop, pass_user_data=True))
    dispatcher.add_handler(MessageHandler(Filters.command, callbacks.unknown_command, pass_user_data=True))
    dispatcher.add_handler(MessageHandler(Filters.text, callbacks.unknown_command, pass_user_data=True))
    dispatcher.add_error_handler(callbacks.error_message)

    logger.info("started polling")

    updater.start_polling()
    updater.idle()


@sightspotter.command()
@click.option(
    '--all', is_flag=True, help='Parse all routes')
@click.option(
    '--overwrite', is_flag=True, help='Overwrite parsed routes')
def parse(**kwargs):
    """Parse new routes from runcity.org
    """
    commuter = config.get_commuter()

    if kwargs.get('overwrite'):
        commuter.execute_script(os.path.join(config.path_to_scripts, 'delete_tables.sql'), commit=True)
        commuter.execute_script(os.path.join(config.path_to_scripts, 'create_tables.sql'), commit=True)

    parser = RouteParser(
        commuter,
        config.parser['url'],
        parse_all=kwargs.get('all'))

    parser.parse()

