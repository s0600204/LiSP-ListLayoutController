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

import logging

from lisp.application import Application
from lisp.core.plugin import Plugin
from lisp.plugins import get_plugin
from lisp.plugins.list_layout_controller.list_layout_controller_settings import ListLayoutControllerSettings
from lisp.plugins.midi import midi_utils
from lisp.plugins.list_layout.layout import ListLayout
from lisp.ui.settings.app_configuration import AppConfigurationDialog

logger = logging.getLogger(__name__)

class ListLayoutController(Plugin):

    Name = 'List Layout MIDI Control'
    Authors = ('Aurélien Cibrario',)
    Depends = ('Midi',)
    Description = 'Cue the show with MIDI! (Voice-messages only.)'

    def __init__(self, app):
        super().__init__(app)
        self.__midi_mapping = {}

        Application().session_created.connect(self._on_session_init)

    def _on_session_init(self):
        if isinstance(Application().layout, ListLayout):

            # Register the settings widget
            AppConfigurationDialog.registerSettingsPage(
                'plugins.list_layout_control', ListLayoutControllerSettings, self.Config)

            self.__keyword_to_action = {
                'gomidimapping': Application().layout._view.goButton.click,
                'stopmidimapping': Application().layout._view.controlButtons.stopButton.click,
                'pausemidimapping': Application().layout._view.controlButtons.pauseButton.click,
                'fadeinmidimapping': Application().layout._view.controlButtons.fadeInButton.click,
                'fadeoutmidimapping': Application().layout._view.controlButtons.fadeOutButton.click,
                'resumemidimapping': Application().layout._view.controlButtons.resumeButton.click,
                'interruptmidimapping': Application().layout._view.controlButtons.interruptButton.click,
                'prevcuemidimapping' : Application().layout._view.listView.selectPrevCue,
                'nextcuemidimapping' : Application().layout._view.listView.selectNextCue
            }

            get_plugin('Midi').input.new_message.connect(self.on_new_midi_message)

    def on_new_midi_message(self, message):
        msg_dict = message.dict()
        if 'velocity' in msg_dict:
            msg_dict.pop('velocity')
        simplified_msg = midi_utils.dict_msg_to_str(msg_dict)

        for keyword, mapping in self.Config._root.items():
            if mapping == simplified_msg:
                self.__keyword_to_action[keyword]()
