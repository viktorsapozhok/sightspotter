# -*- coding: utf-8 -*-

"""Command line interface
"""

import click
import os

from telegram.ext import CommandHandler, ConversationHandler
from telegram.ext import Filters, MessageHandler, Updater

from sightspotter.callbacks import *
from sightspotter.parser import RouteParser
from sightspotter import config, utils

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

    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    entry_points = [
        CommandHandler('start', Start().callback),
        MessageHandler(Filters.location, Location().callback)
    ]

    conversation_states = {
        config.states['location']: [
            MessageHandler(Filters.location, Location().callback)
        ],
        config.states['next']: [
            MessageHandler(Filters.location, Location().callback),
            MessageHandler(Filters.regex(cmd_next), NextSight().callback),
            MessageHandler(Filters.regex(cmd_answer), Answer().callback),
            MessageHandler(Filters.regex(cmd_history), History().callback),
            MessageHandler(Filters.regex(cmd_map), ShowMap().callback)
        ]
    }

    fallbacks = [CommandHandler('stop', stop_callback)]

    conversation_handler = ConversationHandler(
        entry_points=entry_points,
        states=conversation_states,
        fallbacks=fallbacks
    )

    dispatcher.add_handler(conversation_handler)
    dispatcher.add_handler(CommandHandler('help', help_callback))
    dispatcher.add_handler(CommandHandler('start', Start().callback))
    dispatcher.add_handler(CommandHandler('stop', stop_callback))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown_callback))
    dispatcher.add_handler(MessageHandler(Filters.text, unknown_callback))
    dispatcher.add_error_handler(error_callback)

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

