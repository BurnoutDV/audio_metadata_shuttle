#!/usr/bin/env python
# coding: utf-8

# Copyright 2021 by BurnoutDV, <development@burnoutdv.com>
#
# This file is part of AudioMetatagShuttle.
#
# AudioMetatagShuttle is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# AudioMetatagShuttle is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# @license GPL-3.0-only <https://www.gnu.org/licenses/gpl-3.0.en.html>

"""
Some simple functions to display data properly in a console window

Yes i am aware that curses exists, there is probably a library that does exactly what i do here but 5 minutes of
googling yielded nothing that was instantly satisfying or easy enough to use so here i am with my homebrewed methods
that dont advance humanity a bit further. I would like to pretend that i did it to get a bit more familar with python
or something like that. But the sad reality is that i learned almost nothing, i just copy & pasted previous stuff
i wrote before, some random debugs things here and there and probably some stolen StackOverflow stuff i did not even
remember having copied in the first place.
"""
import os
import sys
import logging
from statistics import mean
from collections import defaultdict

# getting terminal size definitive edition
try:
    from shutil import get_terminal_size
except ImportError:
    def get_terminal_size():
        try:
            return os.get_terminal_size()
        except OSError:
            # when executing in PyCharm Debug Window there is no "real" console and you get an Errno 25
            return 80, 24

logger = logging.getLogger(__name__)


def simple_console_view(keys: list, data: list, max_width=0, *column_widths: int):
    r"""
    Displays a simple console view of any given data, will horribly break if too much data is supplied

    :param list keys: list of relevant dictionary keys, used as heading if occuring
    :param list data: list of dict
    :param int max_width: optional maximum width of the whole table
    :param int column_widths: specifies the maximum widht of any one giving heading, 0 is dynamic
    :return: nothing, writes directly to console
    """
    # ! magic numbers
    AVG_TOLERANCE = 3  # * how much bigger as average a column is allowed to be to not get trimmed
    COL_SPACING = 1  # * empty space between columns

    col, row = get_terminal_size()
    if max_width == 0 or max_width > col:
        max_width = col

    # take inventory and average around
    avg_len = defaultdict(float)
    max_len = defaultdict(float)
    set_len = defaultdict(int)
    stat = defaultdict(int)
    for line in data:
        for idx, column in line.items():
            if idx in keys:
                avg_len[idx] = len(column) if 0.0 else avg_len[idx] + (len(column))/2
                max_len[idx] = len(column) if len(column) > max_len[idx] else max_len[idx]  # else without sense
                stat[idx] += 1

    overshoot = (max_width - sum([v for v in max_len.values()]) + len(keys)*COL_SPACING - COL_SPACING) * -1
    if overshoot > 0:
        over_average = mean([v for v in max_len.values()])
        short_cols = [idx for idx, value in avg_len.items() if value > over_average]
        num_short_col = len(short_cols)
        avg_delta = overshoot/num_short_col
        while True:  # a makeshift do..until loop, because i really want a feet controlled loop
            # ? what it does do, it filters out the columns that are in average to long but cannot stand getting
            # ? cut short, there are probably some edge cases were this might fail hard
            short_cols = [idx for idx in short_cols if max_len[idx] - AVG_TOLERANCE > avg_delta]
            avg_delta = overshoot / num_short_col
            if len(short_cols) == num_short_col:
                break
            else:
                num_short_col = len(short_cols)
        corrected = 0
        for idx in keys:
            if idx in short_cols:
                set_len[idx] = int(round(max_len[idx] - avg_delta, 0))
                corrected += max_len[idx] - set_len[idx]
            else:
                set_len[idx] = int(round(max_len[idx], 0))
        if corrected > over_average:
            set_len[keys[-1]] = int(round(set_len[keys[-1]] - (over_average-corrected), 0))
    else:
        set_len = util_convert_to_dict_of_int(max_len)  # for the case that everything would fit nicely it will just put it as it
        # todo: insert stretch functionality here

    header = ""
    for prop in keys:
        header += f"{prop} [{stat[col]}]{' '*set_len[prop]}"[:set_len[prop]] + " "*COL_SPACING
    print(header[:-1])

    for line in data:
        body = ""
        for col in keys:
            if col in line:
                body += f"{line[col]}{' '*set_len[col]}"[:set_len[col]] + " "*COL_SPACING
            else:
                body += f"{' '*set_len[col]}"[:set_len[col]] + " "*COL_SPACING
        print(body[:-COL_SPACING])


def super_simple_progress_bar(current_value, max_value, prefix="", suffix="", out=sys.stdout):
    """
        Creates a simple progress bar without curses, overwrites itself everytime, will break when resizing
        or printing more text
        :param float current_value: the current value of the meter, if > max_value its set to max_value
        :param float max_value: 100% value of the bar, ints
        :param str prefix: Text that comes after the bar
        :param str suffix: Text that comes before the bar
        :param file out: output for the print, creator doesnt know why this exists
        :rtype: None
        :return: normalmente nothing, False and an error line printed instead of the bar
    """
    try:
        current_value = float(current_value)
        max_value = float(max_value)
        prefix = str(prefix)
        suffix = str(suffix)
    except ValueError:
        logger.error("SSimpleProgressBar::Parameter Value error")
        return False
    if current_value > max_value:
        current_value = max_value  # 100%
    max_str, rows = get_terminal_size()
    del rows
    """
     'HTTP |======>                          | 45 / 256 '
     'HTTP |>                                 | 0 / 256 '
     'HTTP |================================| 256 / 256 '
     'HTTP |===============================>| 255 / 256 '
     '[ 5 ]1[ BAR BAR BAR BAR BAR BAR BAR BA]1[   10   ]'
    """
    bar_space = max_str - len(prefix) - len(suffix) - 3  # magic 3 for |, | and >
    bar_length = round((current_value/max_value)*bar_space)
    if bar_length == bar_space:
        arrow = "="
    else:
        arrow = ">"
    the_bar = "="*bar_length + arrow + " "*(bar_space-bar_length)
    print(prefix + "|" + the_bar + "|" + suffix, file=out, end="\r")


def super_simple_progress_bar_clear(out=sys.stdout):
    max_str, rows = get_terminal_size()
    print(" "*max_str, end="\r", file=out)


def util_convert_to_dict_of_int(input: dict):
    """
    Transforms a dictionary of float values to a dictionary of int values
    """
    returnal = defaultdict(int)
    for idx, each in input.items():
        returnal[idx] = int(round(each, 1))
    return returnal
