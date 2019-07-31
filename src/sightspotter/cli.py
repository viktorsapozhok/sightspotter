# -*- coding: utf-8 -*-

"""Command line interface
"""

import click
import os

from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

from db_commuter import SQLiteCommuter
from sightspotter.parser import RouteParser
from sightspotter import callbacks
from sightspotter import config
from sightspotter import utils

logger = config.setup_logger()


@click.group()
def sightspotter():
    """Telegram bot for discovering hidden city gems
    """


@sightspotter.command()
@click.option(
    '--test', is_flag=True, help='Running in test environment')
def poll(test):
    """Start polling
    """
    token = config.test_token if test else config.token

    # commands
    cmd_next = utils.command_pattern(config.button_titles['next'])
    cmd_answer = utils.command_pattern(config.button_titles['answer'])
    cmd_history = utils.command_pattern(config.button_titles['history'])
    cmd_map = utils.command_pattern(config.button_titles['map'])

    updater = Updater(token)
    dispatcher = updater.dispatcher

    entry_points = [
        CommandHandler('start', callbacks.start, pass_user_data=True),
        MessageHandler(Filters.location, callbacks.location, pass_user_data=True)
    ]

    conversation_states = {
        config.states['location']: [
            MessageHandler(Filters.location, callbacks.location, pass_user_data=True)
        ],
        config.states['next']: [
            MessageHandler(Filters.location, callbacks.location, pass_user_data=True),
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
        fallbacks=fallbacks,
        conversation_timeout=config.timeout
    )

    dispatcher.add_handler(conversation_handler)
    dispatcher.add_handler(CommandHandler('help', callbacks.help_message, pass_user_data=True))
    dispatcher.add_handler(CommandHandler('start', callbacks.start, pass_user_data=True))
    dispatcher.add_handler(CommandHandler('stop', callbacks.stop, pass_user_data=True))
    dispatcher.add_handler(MessageHandler(Filters.command, callbacks.unknown_command, pass_user_data=True))
    dispatcher.add_handler(MessageHandler('', callbacks.unknown_command, pass_user_data=True))
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
    commuter = SQLiteCommuter(config.path_to_db)

    if kwargs.get('overwrite'):
        commuter.execute_script(os.path.join(config.path_to_scripts, 'delete_tables.sql'), commit=True)
        commuter.execute_script(os.path.join(config.path_to_scripts, 'create_tables.sql'), commit=True)

    parser = RouteParser(
        commuter,
        config.parser['url'],
        parse_all=kwargs.get('all'))

    parser.parse()

