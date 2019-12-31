# -*- coding: utf-8 -*-

"""Command line interface
"""
import os

import click
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater
)

from . import callbacks, config, utils
from .parser import RouteParser

logger = config.setup_logger()


@click.group()
def sightspotter():
    """Telegram bot for discovering hidden city gems.
    """

    pass


@sightspotter.command()
@click.option('--test', is_flag=True, help='Running in test environment')
def poll(test):
    """Start polling.
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
        CommandHandler('start', callbacks.Start()),
        MessageHandler(Filters.location, callbacks.Location())
    ]

    conversation_states = {
        config.states['location']: [
            MessageHandler(Filters.location, callbacks.Location())
        ],
        config.states['next']: [
            MessageHandler(Filters.location, callbacks.Location()),
            MessageHandler(Filters.regex(cmd_next), callbacks.NextSight()),
            MessageHandler(Filters.regex(cmd_answer), callbacks.Answer()),
            MessageHandler(Filters.regex(cmd_history), callbacks.History()),
            MessageHandler(Filters.regex(cmd_map), callbacks.ShowMap())
        ]
    }

    fallbacks = [CommandHandler('stop', callbacks.stop)]

    conversation_handler = ConversationHandler(
        entry_points=entry_points,
        states=conversation_states,
        fallbacks=fallbacks)

    dispatcher.add_handler(conversation_handler)
    dispatcher.add_handler(CommandHandler('help', callbacks.info))
    dispatcher.add_handler(CommandHandler('start', callbacks.Start()))
    dispatcher.add_handler(CommandHandler('stop', callbacks.stop))
    dispatcher.add_handler(MessageHandler(Filters.command, callbacks.unknown))
    dispatcher.add_handler(MessageHandler(Filters.text, callbacks.unknown))
    dispatcher.add_error_handler(callbacks.error)

    logger.info("started polling")

    updater.start_polling()
    updater.idle()


@sightspotter.command()
@click.option('--overwrite', is_flag=True, help='Overwrite parsed routes')
def parse(**kwargs):
    """Parse new routes.
    """

    commuter = config.get_commuter()

    if kwargs.get('overwrite'):
        commuter.execute_script(
            os.path.join(config.path_to_scripts, 'delete_tables.sql'))
        commuter.execute_script(
            os.path.join(config.path_to_scripts, 'create_tables.sql'))

    RouteParser(commuter, config.parser['url']).parse()
