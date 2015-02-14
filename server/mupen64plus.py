#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2015, Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# emu_archive is a HTML based front end for video game console emulators
# It uses a MIT style license
# It is hosted at: https://github.com/workhorsy/emu_archive
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os, sys

import ini
import emu_runner
import base_console


BUTTON_CODE_MAP = {
	'button_12' : '"hat(0 Up)"', # up
	'button_13' : '"hat(0 Down)"', # down
	'button_14' : '"hat(0 Left)"', # left
	'button_15' : '"hat(0 Right)"', # right
	'button_9' : '"button(7)"', # start
	'button_0' : '"button(0)"', # A
	'button_2' : '"button(2)"', # X
	'button_4' : '"button(4)"', # L Shoulder button
	'button_5' : '"button(5)"', # R Shoulder button
	'button_7' : '"axis(2+)"', # R Trigger
	'button_6' : '"axis(2-)"', # L Trigger
	'axes_0-' : '"axis(0-,0+)"', # L Stick Left
	'axes_0+' : '"axis(0-,0+)"', # L Stick Right
	'axes_1-' : '"axis(1-,1+)"', # L Stick Up
	'axes_1+' : '"axis(1-,1+)"', # L Stick Down
	'axes_2-' : '"axis(4-)"', # R Stick Left
	'axes_2+' : '"axis(4+)"', # R Stick Right
	'axes_3-' : '"axis(3-)"', # R Stick Up
	'axes_3+' : '"axis(3+)"', # R Stick Down
	None : ''
}

class Mupen64Plus(base_console.BaseConsole):
	def __init__(self):
		super(Mupen64Plus, self).__init__('config/mupen64plus.json')

		# Setup the initial map, if there is none
		if not self.button_map:
			self.button_map = {
				'btnUpMupen' : None,
				'btnDownMupen' : None,
				'btnLeftMupen' : None,
				'btnRightMupen' : None,
				'btnStartMupen' : None,
				'btnAMupen' : None,
				'btnBMupen' : None,
				'btnZMupen' : None,
				'btnLShoulderMupen' : None,
				'btnRShoulderMupen' : None,
				'btnStickXMupen' : None,
				'btnStickYMupen' : None,
				'btnCUpMupen' : None,
				'btnCDownMupen' : None,
				'btnCLeftMupen' : None,
				'btnCRightMupen' : None
			}

	def is_installed(self):
		return os.path.isdir('emulators/Mupen64Plus/')

	def _setup_config(self):
		config = {
			'Input-SDL-Control1' : {
				'version' : 2,
				'device' : 0,
				'mode' : 0,
				'plugged' : True,
				'plugin' : 2,
				'mouse' : False,
				'AnalogDeadzone' : '"4096,4096"',
				'AnalogPeak' : '"32768,32768"',
				'DPad R' : BUTTON_CODE_MAP[self.button_map['btnRightMupen']],
				'DPad L' : BUTTON_CODE_MAP[self.button_map['btnLeftMupen']],
				'DPad D' : BUTTON_CODE_MAP[self.button_map['btnDownMupen']],
				'DPad U' : BUTTON_CODE_MAP[self.button_map['btnUpMupen']],
				'Start' : BUTTON_CODE_MAP[self.button_map['btnStartMupen']],
				'Z Trig' : BUTTON_CODE_MAP[self.button_map['btnZMupen']],
				'B Button' : BUTTON_CODE_MAP[self.button_map['btnBMupen']],
				'A Button' : BUTTON_CODE_MAP[self.button_map['btnAMupen']],
				'C Button R' : BUTTON_CODE_MAP[self.button_map['btnCRightMupen']],
				'C Button L' : BUTTON_CODE_MAP[self.button_map['btnCLeftMupen']],
				'C Button D' : BUTTON_CODE_MAP[self.button_map['btnCDownMupen']],
				'C Button U' : BUTTON_CODE_MAP[self.button_map['btnCUpMupen']],
				'R Trig' : BUTTON_CODE_MAP[self.button_map['btnRShoulderMupen']],
				'L Trig' : BUTTON_CODE_MAP[self.button_map['btnLShoulderMupen']],
				'Mempak switch' : '""',
				'Rumblepak switch' : '""',
				'X Axis' : BUTTON_CODE_MAP[self.button_map['btnStickXMupen']],
				'Y Axis' : BUTTON_CODE_MAP[self.button_map['btnStickYMupen']],
				'name' : '"Custom pad"'
			}
		}

		ini.write_ini_file(os.path.expanduser('~/AppData/Roaming/Mupen64Plus/mupen64plus.cfg'), config)

	def run(self, path, binary):
		self._setup_config()

		# Run the game
		os.chdir("emulators/Mupen64Plus/")
		game_path = self.goodJoin("../../", path + '/' + binary)
		command = '"Mupen64plus.exe" --fullscreen "' + game_path + '"'
		runner = emu_runner.EmuRunner(command, 'Mupen64Plus', full_screen, full_screen_alt_enter=False)
		runner.run()
		os.chdir("../..")

