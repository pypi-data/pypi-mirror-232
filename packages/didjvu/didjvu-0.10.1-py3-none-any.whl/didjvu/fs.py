# encoding=UTF-8

# Copyright © 2009-2018 Jakub Wilk <jwilk@jwilk.net>
#
# This file is part of didjvu.
#
# didjvu is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# didjvu is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.

"""
Filesystem functions
"""

import os

_BLOCK_SIZE = 1 << 20  # 1 MiB


def copy_file(input_file, output_file):
    length = 0
    while True:
        block = input_file.read(_BLOCK_SIZE)
        if not block:
            break
        length += len(block)
        output_file.write(block)
    return length


def replace_ext(filename, ext):
    return f'{os.path.splitext(filename)[0]}.{ext}'


__all__ = [
    'copy_file',
    'replace_ext',
]

# vim:ts=4 sts=4 sw=4 et
