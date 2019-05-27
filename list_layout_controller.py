# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2016-2017 Aurélien Cibrario <aurelien.cibrario@gmail.com>
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

"""Plugin for controlling the List Layout via MIDI.

This plugin adds the ability to control various functions in the List Layout
(Go, Stop, Back, Forward, ...) with MIDI voice messages.

Code based on Yinameah's work in Pull Request #80.
"""

import logging

# pylint: disable=import-error
from lisp.core.plugin import Plugin
from lisp.plugins import get_plugin
from lisp.plugins.midi import midi_utils
from lisp.plugins.list_layout.layout import ListLayout
from lisp.ui.settings.app_configuration import AppConfigurationDialog

from .list_layout_controller_settings import ListLayoutControllerSettings

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
class ListLayoutController(Plugin):
    """The primary class of this Plugin."""

    Name = 'List Layout MIDI Control'
    Authors = ('Aurélien Cibrario',)
    Depends = ('Midi',)
    Description = 'Cue the show with MIDI! (Voice-messages only.)'

    def __init__(self, app):
        super().__init__(app)
        self.__midi_mapping = {}
        self.__keyword_to_action = {}

        app.session_created.connect(self._on_session_init)
        app.session_before_finalize.connect(self._on_session_deinit)

    def _on_session_init(self):
        if not isinstance(self.app.layout, ListLayout):
            return

        # Register the settings widget
        AppConfigurationDialog.registerSettingsPage(
            'plugins.list_layout_control', ListLayoutControllerSettings, self.Config)

        layout = self.app.layout
        self.__keyword_to_action = {
            'go': layout.view.goButton.click,
            'stop': layout.view.controlButtons.stopButton.click,
            'pause': layout.view.controlButtons.pauseButton.click,
            'fadeIn': layout.view.controlButtons.fadeInButton.click,
            'fadeOut': layout.view.controlButtons.fadeOutButton.click,
            'resume': layout.view.controlButtons.resumeButton.click,
            'interrupt': layout.view.controlButtons.interruptButton.click,
            'prevCue': lambda: layout.set_standby_index(layout.standby_index() - 1),
            'nextCue': lambda: layout.set_standby_index(layout.standby_index() + 1),
        }

        get_plugin('Midi').input.new_message.connect(self.on_new_midi_message)

    def _on_session_deinit(self):
        self.__keyword_to_action = {}

    def on_new_midi_message(self, message):
        """Called when a new MIDI message is recieved on the connected input."""

        msg_dict = message.dict()
        if 'velocity' in msg_dict:
            msg_dict.pop('velocity')
        simplified_msg = midi_utils.dict_msg_to_str(msg_dict)

        for keyword, mapping in self.Config['mappings'].items():
            if mapping == simplified_msg:
                self.__keyword_to_action[keyword]()
