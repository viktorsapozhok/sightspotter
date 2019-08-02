# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup

version = '0.1.0'

root_dir = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(root_dir, 'README.md'), 'r', encoding='utf-8') as f:
        long_description = f.read()
except IOError:
    long_description = ''

# init version
version_path = os.path.join(root_dir, 'src', 'sightspotter', 'version.py')
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
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    packages=find_packages('src'),
    install_requires=[
        'beautifulsoup4',
        'Click',
        'db-commuter>=0.1.7',
        'numpy',
        'pandas',
        'python-dotenv',
        'python-telegram-bot>=12.0.0b1',
        'requests',
        'tqdm'
    ],
    entry_points='''
        [console_scripts]
        sightspotter=sightspotter.cli:sightspotter
    ''',
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]
)
