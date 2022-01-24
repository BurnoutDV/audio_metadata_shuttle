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
import copy
import logging
from math import ceil, floor
from statistics import mean, median, pvariance, pstdev
# ? variance assumes a sample, pvariance is when the values we have are ALL values
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

# ! magic numbers
__AVG_TOLERANCE = 3  # * how much bigger as average a column is allowed to be to not get trimmed
__COL_SPACING = 1  # * empty space between columns


def _calc_console_widths_average_method(headers: list, data: list, max_width=0, *column_width: int):
    global __AVG_TOLERANCE, __COL_SPACING
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
            stat[idx] += 1
            if idx in headers:
                avg_len[idx] = len(column) if 0.0 else avg_len[idx] + (len(column)) / 2
                max_len[idx] = len(column) if len(column) > max_len[idx] else max_len[idx]  # else without sense

    # thin out keys for things that do not exist in the data (aka. ignored headers duo inexisting data)
    new_keys = []
    for key in headers:
        if stat[key] > 0:
            new_keys.append(key)
    keys = new_keys

    overshot = (max_width - sum([v for v in max_len.values()]) - (len(keys) - 1) * __COL_SPACING) * -1
    if overshot > 0:
        over_average = mean([v for v in max_len.values()])
        short_cols = [idx for idx, value in avg_len.items() if value > over_average]
        num_short_col = len(short_cols)
        avg_delta = ceil(overshot / num_short_col)
        while True:  # a makeshift do..until loop, because i really want a feet controlled loop
            # ? what it does do, it filters out the columns that are in average to long but cannot stand getting
            # ? cut short, there are probably some edge cases were this might fail hard
            short_cols = [idx for idx in short_cols if max_len[idx] - __AVG_TOLERANCE > avg_delta]
            avg_delta = ceil(overshot / num_short_col)
            if len(short_cols) == num_short_col:
                break
            else:
                num_short_col = len(short_cols)
        corrected = 0
        for idx in keys:
            if idx in short_cols:
                # ! average difference
                set_len[idx] = int(max_len[idx] - avg_delta)
                # set_len[idx] = int(round(max_len[idx]-(max_len[idx]/num_short_col), 0))
                corrected += max_len[idx] - set_len[idx]
            else:
                set_len[idx] = int(max_len[idx])
        if corrected > overshot:  # we overcorrected, adding some stuff to the smallest columns
            smallest = keys[0]
            for idx in short_cols:
                if set_len[smallest] > set_len[idx]:
                    smallest = idx
            set_len[smallest] = set_len[smallest] + (overshot - corrected)
        # it should never undershot
    elif overshot < 0:
        # includes length of headers as well
        max2_len = copy.copy(max_len)
        for idx in keys:
            max2_len[idx] = len(idx) if len(idx) > max2_len[idx] else max2_len[idx]
        new_shot = (max_width - sum([v for v in max2_len.values()]) - (len(keys) - 1) * __COL_SPACING) * -1
        if new_shot <= 0:  # enough space to add to all headers AND additional space (might be 0)
            max_len = max2_len
            overshot = new_shot
            avg_add = floor(overshot / len(keys) * -1)
            for idx in keys:
                set_len[idx] = int(max_len[idx] + avg_add)
            # a convoluted way to reduce the longest element by 1
            gen_width = sum([x for x in set_len.values()])
            if gen_width > max_width:
                biggest = keys[0]
                for idx in keys:
                    if set_len[biggest] > set_len[idx]:
                        biggest = idx
                set_len[biggest] -= gen_width - max_width
        else:  # overshot is not enough to add enough empty space to all columns so its headers can be displayed
            free_space = overshot * -1
            while True:  # uses up the free space as much as possible
                for idx in keys:
                    if len(idx) > max_len[idx]:
                        delta = len(idx) - max_len[idx]
                        if delta < free_space:
                            max_len[idx] += delta
                            free_space -= delta
                        else:  # just use all the space we got left
                            max_len[idx] += free_space
                            free_space = 0
                    set_len[idx] = int(max_len[idx])
                if free_space <= 0:
                    break
    else:  # exactly on point
        set_len = util_convert_to_dict_of_int(max_len)
        # for the case that everything would fit nicely it will just put it as it
        # todo: insert stretch functionality here
    return set_len, stat


def _calc_console_widths_absolute_method(headers: list, data: list, max_width=0, *column_widths: int):
    global __AVG_TOLERANCE, __COL_SPACING
    col, row = get_terminal_size()
    if max_width == 0 or max_width > col:
        max_width = col
    # default things we use later
    max1_len = defaultdict(int)
    max2_len = defaultdict(int)
    val_list = defaultdict(list)
    set_len = defaultdict(int)
    stat = defaultdict(int)
    med_len = defaultdict(float)

    # maximum needed space
    for line in data:
        for col in headers:
            if col in line:
                stat[col] += 1
                if col in headers:
                    tmp = len(line[col])
                    max1_len[col] = tmp if tmp > max1_len[col] else max1_len[col]
                    val_list[col].append(tmp)
    # in case that the headers are bigger than the content
    max2_len = copy.copy(max1_len)
    for val in headers:
        max2_len[val] = len(val) if len(val) > max2_len[val] else max2_len[val]
    # various numbers
    disp_cols = [x for x in headers if stat[x] > 0]  # columns that get displayed
    num_col = len(disp_cols)
    space_len = (num_col-1) * __COL_SPACING
    min_space = num_col + space_len
    max_space = sum([x for x in max1_len.values()]) + space_len
    avail_space = max_width - space_len

    missing_space = max_space - max_width
    # * edge case 1 - available space is not enough to even display all columns
    # * edge case 2 - there is enough space to show all content-lines
    # * edge case 3 - there is enough space to show all header & content-lines
    # * 'edge' case 4 - there is not enough space for all columns (this is what i actually expected to happen)
    # median of length, longest get available free space
    med_len = {col: median(val_list[col]) for col in disp_cols if col in val_list}
    var_len = {col: pvariance(val_list[col]) for col in disp_cols if col in val_list}
    div_len = {col: pstdev(val_list[col]) for col in disp_cols if col in val_list}
    # sort columns by highest value
    med_len = {k: v for k, v in sorted(med_len.items(), key=lambda item: item[1], reverse=True)}
    avg_len = mean([x for x in med_len.values()])  # technically the average of the median
    long_cols = [col for col in disp_cols if max1_len[col] > avg_len]
    num_long_col = len(long_cols)
    vd_per_col = ceil(missing_space / num_long_col)  # void per column ( void as 'opposite' of space)
    abs_vd = missing_space / num_long_col
    while True:
        long_cols = [col for col in long_cols if max1_len[col] > vd_per_col]  # every column has at least 1 char width
        if len(long_cols) == num_long_col:
            break
        else:
            num_long_col = len(long_cols)
            vd_per_col = ceil(missing_space / num_long_col)
    for col in disp_cols:
        if col in long_cols:
            set_len[col] = max1_len[col]-vd_per_col
        else:
            set_len[col] = max1_len[col]
    # filling up to full width or taking from to make sure its always the entire line
    col = next(iter(med_len.keys()))
    set_len[col] += sum([x for _, x in set_len.items()]) - avail_space
    print(f"{max_width=}, {missing_space=}, {vd_per_col=}({abs_vd:.2f}), Rest={sum([x for _, x in set_len.items()])}")
    print("med", dict(med_len))
    print("var", ", ".join([f"'{k}': {v:.2f}" for k, v in var_len.items()]))
    print("div", ", ".join([f"'{k}': {v:.2f}" for k, v in div_len.items()]))
    print("set", dict(set_len))
    print("max", dict(max1_len))
    print("dif", {x: max1_len[x]-set_len[x] for x in disp_cols})
    return set_len, stat


def calc_distribution(val_list: dict, method="median"):
    if method == "average" or method == "mean":
        lens = {col: mean(val_list[col]) for col in val_list}
    else:  # method == "median"
        lens = {col: median(val_list[col]) for col in val_list}
    total_len = sum([x for x in lens.values()])
    return {col: x/total_len for col, x in lens.items()}


def simple_console_view(keys: list, data: list, max_width=0, *column_widths: int):
    r"""
    Displays a simple console view of any given data, will horribly break if too much data is supplied

    :param list keys: list of relevant dictionary keys, used as heading if occuring
    :param list data: list of dict
    :param int max_width: optional maximum width of the whole table
    :param int column_widths: specifies the maximum widht of any one giving heading, 0 is dynamic
    :return: nothing, writes directly to console
    """
    global __AVG_TOLERANCE, __COL_SPACING

    set_len, stat = _calc_console_widths_absolute_method(keys, data, max_width)
    #set_len, stat = _calc_console_widths_average_method(keys, data, max_width)
    header = ""
    for prop in keys:
        header += f"{prop} [{stat[prop]}]{' '*set_len[prop]}"[:set_len[prop]] + " "*__COL_SPACING
    print(header[:-__COL_SPACING])

    for line in data:
        body = ""
        for col in keys:
            if col in line:
                body += f"{line[col]}{' '*set_len[col]}"[:set_len[col]] + " "*__COL_SPACING
            else:
                body += f"{' '*set_len[col]}"[:set_len[col]] + " "*__COL_SPACING
        print(body[:-__COL_SPACING])
        break


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
