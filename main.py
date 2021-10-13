#!/usr/bin/env python
# coding: utf-8

# Copyright 2021 by BurnoutDV, <developer@burnoutdv.com>
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

from pathlib import Path
import mutagen
import json

__AUDIO_FILETYPES__ = ["ogg", "aac", "m4a", "mp3", "flac"]
__BDV_TAGS__ = ["TITLE", "ARTIST", "ALBUM", "TRACKNUMBER", "DISCNUMBER", "GENRE", "DESCRIPTION", "VERSION", "DATE"]
filetype_filter = ["[mM][pP][3]"]


def _generate_filetype_pattern(*filetypes):
    global filetype_filter
    filetype_filter = []
    for each in filetypes:
        singular_pattern = "*."
        for char in each:
            if char.isalpha():
                singular_pattern += f"[{char.lower()}{char.upper()}]"
            else:
                singular_pattern += f"[{char}]"
        filetype_filter.append(singular_pattern)


def crawl_folder(folder_path):
    all_paths = []
    for x in filetype_filter:
        all_paths.extend(list(Path(folder_path).rglob(x)))
    return all_paths


if __name__ == "__main__":
    _generate_filetype_pattern(*__AUDIO_FILETYPES__)
    paths = crawl_folder(".")
    test_dict = []
    for each in paths:
        meta = mutagen.File(f"./{each}")
        test_dict.append({k: meta[k] for k in __BDV_TAGS__ if k in meta})
    print(test_dict)
    json.dumps(test_dict, indent=2)
