#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2015, Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# emulators-online is a HTML based front end for video game console emulators
# It uses the GNU AGPL 3 license
# It is hosted at: https://github.com/workhorsylegacy/emulators-online
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os, sys

import ini
import emu_runner
import base_console


class PCSXR(base_console.BaseConsole):
	def __init__(self):
		super(PCSXR, self).__init__('config/pcsxr.json')

	def is_installed(self):
		return os.path.isdir('emulators/pcsxr/')

	def run(self, path, binary):
		os.chdir("emulators/pcsxr/")

		# Figure out if running a game or not
		command = None
		full_screen = False
		if path and binary:
			game_path = self.goodJoin('../../', path + '/' + binary)
			command = '"pcsxr.exe" -nogui -cdfile "' + game_path + '"'
			full_screen = True
		else:
			command = '"pcsxr.exe"'
			full_screen = False

		# Run the game
		runner = emu_runner.EmuRunner(command, 'PCSXR', full_screen, full_screen_alt_enter=True)
		runner.run()
		os.chdir("../..")

