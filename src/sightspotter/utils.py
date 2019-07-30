# -*- coding: utf-8 -*-

"""Utilities
"""

import re


def command_pattern(cmd):
    return re.compile('^(' + cmd + ')$', re.I)

