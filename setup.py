# -*- coding: utf-8 -*-
from os import path
from setuptools import setup

version = '0.1.1'

root_dir = path.abspath(path.dirname(__file__))

try:
    with open(
            path.join(root_dir, 'README.md'),
            mode='r',
            encoding='utf-8'
    ) as f:
        long_description = f.read()
except IOError:
    long_description = ''

# init version
version_path = path.join(root_dir, 'bot', 'version.py')
with open(version_path, 'w') as f:
    f.write('__version__ = "{}"\n'.format(version))

setup(
    name='sightspotter',
    version=version,
    description='Sightspotter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Alex Piskun',
    author_email='piskun.aleksey@gmail.com',
    url='https://github.com/viktorsapozhok/sightspotter',
    packages=['bot'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'beautifulsoup4==4.8.0',
        'click',
        'db-commuter==0.1.13',
        'numpy',
        'pandas>=0.24.0',
        'python-dotenv',
        'python-telegram-bot==12.0.0b1',
        'requests==2.22.0',
        'tqdm'
    ],
    entry_points={
        'console_scripts': [
            'sightspotter=bot.cli:sightspotter'
        ]
    },
    extras_require={
        'test': ['pytest', 'tox>=3.10.0']
    },
    python_requires='>=3.6'
)
