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

import logging
from audiolib import test_all
import sys
from pathlib import Path
from statics import __version__, __appauthor__, __appname__
from gui_logic import Run

logging.basicConfig(format='[%(asctime)s] %(levelname)s:%(message)s', level=logging.INFO)
#logging.basicConfig(format='%(message)s', level=logging.DEBUG)


if __name__ == "__main__":
    if len(sys.argv) > 0:
        if sys.argv[1] == "gui":
            Run()
        elif len(sys.argv) == 2:
            print(sys.argv)
            basepath = sys.argv[1]
            if not Path(basepath).is_dir():
                logging.critical("Path cannot be accessed")
                basepath = "."

            test_all(basepath)
        else:
            test_all()
    else:
        Run()

