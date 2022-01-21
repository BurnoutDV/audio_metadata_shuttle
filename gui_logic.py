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

import sys
from gui_description import ShuttleMainWindow
from statics import __version__, __appauthor__, __appname__
from PySide2 import QtWidgets, QtCore
from PySide2.QtGui import QIcon

# Windows Stuff for Building under Windows
try:
    from PySide2.QtWinExtras import QtWin
    myappid = f'BDV.shuttle.{__version__}'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class AudioMetatagShuttle(QtWidgets.QMainWindow, ShuttleMainWindow):
    """
    your long doc text here
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBaseSize(1600, 900)
        self.setMinimumSize(1600, 900)
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint & QtCore.Qt.WindowMaximizeButtonHint)
        self.setWindowTitle(f"Audio Metatag Shuttle - {__version__}")

        # ! builds central layout, one liner but with import changes
        self.build_shuttle_ui(self)

        # Events

    def closeEvent(self, event):
        """
        Capture Event in case we want to do something when the windows gets closed
        """
        event.accept() #  event.ignore()


def Run():
    App = QtWidgets.QApplication(sys.argv)
    App.setWindowIcon(QIcon('./app_icon.png'))
    Window = AudioMetatagShuttle()
    Window.show()
    try:
        sys.exit(App.exec_())
    except KeyboardInterrupt:
        sys.exit()