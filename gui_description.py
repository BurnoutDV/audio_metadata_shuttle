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

import logging
import os
import sys

from PySide6.QtGui import QStandardItemModel, QStandardItem, QFontDatabase, QIcon, QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextDocument, QPalette
from PySide6.QtWidgets import *
from PySide6 import QtCore, QtWidgets
from statics import __version__, __appauthor__, __appname__

logger = logging.getLogger(__name__)


def resource_path(relative_path: str) -> str:
    """
    Returns the path to a ressource, normally just echos, but when this is packed with PyInstall there wont be any
    additional files, therefore this is the middleware to access packed data
    :param relative_path: relative path to a file
    :return: path to the file
    :rtype: str
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class ShuttleMainWindow(object):

    def build_shuttle_ui(self, MainWindow: QMainWindow):
        self.main_layout = QVBoxLayout()
        main_line1_layout = QHBoxLayout()
        self.SavedDataView = QTableView()
        self.FolderView = QTreeView()
        ## adding
        main_line1_layout.addWidget(self.SavedDataView)
        main_line1_layout.addWidget(self.FolderView)

        main_line2_layout = QHBoxLayout()
        self.MatchView = QListView()
        self.Button = QPushButton("bla")
        ## adding
        main_line2_layout.addWidget(self.MatchView)
        main_line2_layout.addWidget(self.Button)


        # putting together the interface
        self.main_layout.addLayout(main_line1_layout)
        self.main_layout.addLayout(main_line2_layout)

        dummyWidget = QWidget()
        dummyWidget.setLayout(self.main_layout)
        MainWindow.setCentralWidget(dummyWidget)
