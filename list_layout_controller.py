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
#from lisp.plugins.list_layout.settings import ListLayoutSettings
from lisp.plugins.list_layout_controller.list_layout_controller_settings import ListLayoutControllerSettings
from lisp.plugins.midi import midi_utils
from lisp.plugins.list_layout.layout import ListLayout
from lisp.ui.settings.app_configuration import AppConfigurationDialog
'''
from lisp.core.configuration import config

'''

logger = logging.getLogger(__name__)

class ListLayoutController(Plugin):

    Name = 'List Layout MIDI Control'
    Authors = ('Aurélien Cibrario',)
    Depends = ('Midi',)
    Description = 'Cue the show with MIDI! (Voice-messages only.)'

    def __init__(self, app):
        super().__init__(app)
       
         # Register the settings widget
        AppConfigurationDialog.registerSettingsPage(
            'plugins.list_layout_control', ListLayoutControllerSettings, self.Config)

        self.__midi_mapping = midi_utils.str_msg_to_dict(self.Config['gomidimapping'])

        Application().session_created.connect(self._on_session_init)
        logger.debug('init of plugin done')

    def _on_session_init(self):
        if isinstance(Application().layout, ListLayout):
            get_plugin('Midi').input.new_message.connect(self.do_something_when_midi_triggered)
            logger.debug('midi signal connected !')

    def do_something_when_midi_triggered(self, message):
        msg = midi_utils.str_msg_to_dict(str(message))

        if message.type != 'program_change':
            logger.debug(f"msg from config : {self.__midi_mapping}")
            logger.debug(f"msg received : {msg}")
            return

        if msg['channel'] == self.__midi_mapping['channel']:
            if msg['program'] == self.__midi_mapping['program']:
                Application().layout.go()
                logger.info('Trigger activated')

