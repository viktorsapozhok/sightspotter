# -*- coding: utf-8 -*-

"""Configuration parameters
"""

import logging
import os

from dotenv import load_dotenv

from db_commuter import SQLiteCommuter

root_dir = os.path.dirname(os.path.abspath(os.path.join(__file__, '../..')))

# path to database
path_to_db = os.path.join(root_dir, 'db', 'sightspotter.sqlite3')
# path to .env file
path_to_env = os.path.join(root_dir, 'app', 'secret.env')
# path to scripts
path_to_scripts = os.path.join(root_dir, 'scripts')

# load secrets into environ
load_dotenv(path_to_env)

# bot API token (production)
token = os.getenv('TOKEN')
# bot API token (testing)
test_token = os.getenv('TEST_TOKEN')

# conversation states
states = {
    'location': 0,
    'next': 1
}

max_dist = 10
n_next = 10
# timeout (seconds)
timeout = 1200

# new line variable
nl = '\n'

# bot messages
messages = {
    'start':
        f'Чтобы начать, пришлите свое местоположение:{nl + nl}'
        f'- кнопка \"Отправить геолокацию\"{nl}'
        f'(в случае ошибки нужно разрешить в настройках доступ приложения к службам геолокации){nl + nl}'
        f'- либо отправьте местоположение через аттачмент (значок скрепки)',
    'stop':
        f'Бот остановлен',
    'not_found':
        f'Не найдено ни одного места в радиусе {max_dist} км',
    'next_not_found':
        f'Больше ничего не найдено в радиусе {max_dist} км{nl}'
        f'Пришлите новое местоположение',
    'max_next_events':
        f'Пришлите новое местоположение',
    'help':
        f'Поддерживаются следующие команды:{nl}'
        f'/start - запустить бота{nl}'
        f'/stop - остановить бота{nl}'
        f'/help - открыть справку',
    'unknown':
        f'Некорректный запрос, возможно бот отключился, нажмите /start',
    'answer_not_found':
        f'Ответ не найден'
}

button_titles = {
    'next':
        'Дальше',
    'answer':
        'Ответ',
    'history':
        'История',
    'map':
        'Показать карту',
    'location':
        'Отправить геолокацию'
}

# parser config params
parser = {
    'url': 'https://www.runcity.org/ru/events/archive/',
    'min_length_addr': 5,
    'min_length_descr': 5,
    'min_length_quest': 3,
    'min_length_answer': 1,
    'stop_words_addr': ['загадка', 'анаграмма'],
    'stop_words_descr': ['внимание'],
    'stop_words_quest': ['подпись судьи', 'старт', 'финиш'],
    'remove_words_hist': ['историческая справка', 'Историческая справка']
}

# database tables parameters
db_tables = {
    'routes': {
        'columns': ['event', 'year', 'route']
    },
    'sights': {
        'columns': ['sight_id', 'lat', 'lon', 'event', 'cp_id',
                    'address', 'description', 'quest', 'answer', 'year']
    },
    'history': {
        'columns': ['sight_id', 'event', 'cp_id', 'history']
    }
}


def setup_logger():
    """Configure logger
    """
    logger = logging.getLogger('sightspotter')

    # set stream handler format
    stream_formatter = logging.Formatter(
        '%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # add stdout handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)

    return logger


def get_commuter():
    return SQLiteCommuter(path_to_db)

