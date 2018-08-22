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

from PyQt5.QtCore import QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QGroupBox, QLabel, QPushButton, QMessageBox, QFormLayout

from lisp.plugins import get_plugin
from lisp.plugins.midi import midi_utils
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate

class ListLayoutControllerSettings(QGroupBox, SettingsPage):
    Name = QT_TRANSLATE_NOOP('ConfigurationPageName', 'List Layout Controller')

    MappingsMap = {
        'go': {
            'caption': 'GO control'
        },
        'stop': {
            'caption': 'Stop All control'
        },
        'pause': {
            'caption': 'Pause control'
        },
        'fadeIn': {
            'caption': 'Fade In control'
        },
        'fadeOut': {
            'caption': 'Fade Out control'
        },
        'resume': {
            'caption': 'Resume control'
        },
        'interrupt': {
            'caption': 'Interrupt control'
        },
        'prevCue': {
            'caption': 'Previous Cue control'
        },
        'nextCue': {
            'caption': 'Next Cue control'
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setLayout(QFormLayout())
        self.setTitle(translate('ListLayoutController', 'Midi Mappings'))

        for mapDef in self.MappingsMap.values():
            mapDef['label'] = QLabel(self)
            mapDef['button'] = QPushButton(self)
            mapDef['button'].clicked.connect(self.__learn_midi)
            self.layout().addRow(mapDef['label'], mapDef['button'])

        self.retranslateUi()

    def retranslateUi(self):
        for mapDef in self.MappingsMap.values():
            mapDef['label'].setText(translate('ListLayoutController', mapDef['caption']))
            mapDef['button'].setText(translate('ListLayoutController', 'No MIDI mapping'))

    def getSettings(self):
        noMidiCaption = translate('ListLayoutController', 'No MIDI mapping')
        settings = { 'mappings': {} }
        for mapId, mapDef in self.MappingsMap.items():
            if mapDef['button'].text() != noMidiCaption:
                settings['mappings'][mapId] = mapDef['button'].text()
            else:
                settings['mappings'][mapId] = ""
        return settings

    def loadSettings(self, settings):
        for mapId, mapDef in self.MappingsMap.items():
            if settings['mappings'][mapId]:
                mapDef['button'].setText(settings['mappings'][mapId])

    def __learn_midi(self):
        handler = get_plugin('Midi').input
        handler.alternate_mode = True

        def received_message(msg):
            msg_dict = midi_utils.str_msg_to_dict(str(msg))
            if 'velocity' in msg_dict:
                msg_dict.pop('velocity')

            simplified_msg = midi_utils.dict_msg_to_str(msg_dict)
            self.sender().setText(simplified_msg)
            self.midi_learn.accept()

        handler.new_message_alt.connect(received_message)

        self.midi_learn = QMessageBox(self)
        self.midi_learn.setText(translate('ControllerMidiSettings',
                                          'Listening MIDI messages ...'))
        self.midi_learn.setIcon(QMessageBox.Information)
        self.midi_learn.setStandardButtons(QMessageBox.Cancel)

        result = self.midi_learn.exec_()
        if result == QMessageBox.Cancel:
            self.sender().setText(translate('ListLayoutController', 'No MIDI mapping'))

        handler.new_message_alt.disconnect(received_message)
        handler.alternate_mode = False
