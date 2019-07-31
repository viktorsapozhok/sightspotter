# -*- coding: utf-8 -*-

"""Utilities
"""

import re


def command_pattern(cmd):
    return re.compile('^(' + cmd + ')$', re.I)


def get_sights_count(sights):
    if sights is None:
        return 0
    else:
        return len(sights)

