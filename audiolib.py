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

# https://mutagen.readthedocs.io/en/latest/user/gettingstarted.html
import sys
from pathlib import Path
from collections import defaultdict
from statics import __version__, __appauthor__, __appname__
import mutagen, mutagen.easyid3
import logging
import re
import time
from console_util import simple_console_view

logger = logging.getLogger(__name__)

__BDV_TAGS__ = ["title", "artist", "album", "tracknumber", "discnumber", "genre", "description", "version", "date"]
filetype_filter = ["[mM][pP][3]"]


def _generate_filetype_pattern(*filetypes):
    global filetype_filter
    filetype_filter = []
    for key in filetypes:
        singular_pattern = "*."
        for char in key:
            if char.isalpha():
                singular_pattern += f"[{char.lower()}{char.upper()}]"
            else:
                singular_pattern += f"[{char}]"
        filetype_filter.append(singular_pattern)


def multi_crawl_folder(folder_path, *filetypes) -> list:
    """
    Crawls a given folder for more than one filetype and gives a list of all the files
    :param str folder_path: Path to a folder
    :param str filetypes: glob file extension filter, will be global variable filetype_filter.values() if not set
    :rtype: list[Path]
    :return: a list of which each element is a Path-Object to the found files
    """
    global filetype_filter
    if not filetypes:
        filetypes = filetype_filter
    all_paths = []
    for x in filetypes:
        all_paths.extend(list(Path(folder_path).rglob(x)))
    return all_paths


def equalize_tracknumber(tracknumber: str):
    """
    Removes and equalizes the most common variants of tracknumber deviations i could find in my local library.
    The desired target format will be a simple number without a trailing zero
    Examples for things i found: '02', '#9', '12/12', '02/12'
    """
    tracknumber = str(tracknumber)  # i  dont believe for one second i only get strings
    if re.search(r"^0\d*$", tracknumber):
        return tracknumber[1:]
    if re.search(r"^\d*$", tracknumber):
        return tracknumber  # normal number "15"
    if re.search(r"^0\d*/\d*$", tracknumber):
        return tracknumber.split("/")[0][1:]
    if re.search(r"^\d*/\d*$", tracknumber):
        return tracknumber.split("/")[0]
    return tracknumber.strip()


def standardize_id3(file_path):
    relevant_keys = ["title", "album", "date", "artist", "discnumber", "tracknumber"]
    try:
        audio = mutagen.easyid3.EasyID3(file_path)
        simple_tags = defaultdict(None)
        for key in relevant_keys:
            if key in audio:
                if len(audio[key]) == 1:
                    simple_tags[key] = audio[key][0]
                else:
                    simple_tags[key] = audio[key]
        # ? i only care for one number, equalizer here
        if 'tracknumber' not in simple_tags and 'discnumber' in simple_tags:
            simple_tags['tracknumber'] = simple_tags['discnumber']
        if 'tracknumber' in simple_tags:
            simple_tags['tracknumber'] = equalize_tracknumber(simple_tags['tracknumber'])
            if len(simple_tags['tracknumber']) > 2:
                logger.debug(f"Tracknumber longer than 2 digits: [{simple_tags.get('artist', '?')}-{simple_tags.get('title', '?')}]")
        return simple_tags
    except mutagen.MutagenError as e:
        logger.error(f"MutagenException: {e}")


def recurse_folder(folder_path):
    paths = multi_crawl_folder(folder_path)
    test_dict = []
    for each in paths:
        rel_file_path = Path.joinpath(Path(folder_path), Path(each))
        meta = mutagen.File(rel_file_path)
        print("\nitems")
        for key, item in meta.items():
            print(f"{str(key)[:128]}:{str(item)[:128]}", end="  ")
        # test_dict.append({k: meta[k] for k in __BDV_TAGS__ if k in meta})
        test_dict.append(meta)
    simple_console_view(__BDV_TAGS__, test_dict)


def count_trackvariants(folder_path, file_filter="*.[mM][pP][3]"):
    files = multi_crawl_folder(folder_path, file_filter)
    variants = defaultdict(int)
    for audio in files:
        full_meta = standardize_id3(audio)
        variants[full_meta.get('tracknumber', "none")] += 1
    return variants


__AUDIO_FILETYPES__ = {"ogg": None, "aac": None, "m4a": None, "mp3": standardize_id3, "flac": None}


def test_all():
    _generate_filetype_pattern(*__AUDIO_FILETYPES__.keys())
    if len(sys.argv) == 2:
        basepath = sys.argv[1]
        if not Path(basepath).is_dir():
            print("Given Path cannot be accessed")
            exit()
    else:
        basepath = "."
    # recurse_folder(base_path)
    start = time.time_ns()  # ! time keeping start

    all_files = multi_crawl_folder(basepath, *filetype_filter)
    all_metadata = []
    for sng_file in all_files:
        if __AUDIO_FILETYPES__[str(sng_file.suffix[1:]).lower()] is not None:
            logger.debug("MAIN::found a compatible procedure")
            pure_data = __AUDIO_FILETYPES__[str(sng_file.suffix[1:]).lower()](sng_file)
        else:
            logger.debug("MAIN::no suitable procedure found, fallback")
            raw_data = mutagen.File(sng_file)
            pure_data = {}
            for my_tags in __BDV_TAGS__:
                for raw_tag in raw_data.keys():
                    if raw_tag.lower() == my_tags:
                        pure_data[my_tags] = raw_data[raw_tag]
                        if isinstance(pure_data[my_tags], list) and len(pure_data[my_tags]) == 1:
                            pure_data[my_tags] = pure_data[my_tags][0]
        if pure_data:
            all_metadata.append(pure_data)
    simple_console_view(__BDV_TAGS__, all_metadata)

    # variants = count_trackvariants(".")
    # print(json.dumps({k: v for k, v in sorted(variants.items(), key=lambda item: item[1])}, indent=3))

    stop = time.time_ns()  # ! time keeping stopped
    print("")
    print(f"Difference: {str((stop - start) / 1000000)}ms")