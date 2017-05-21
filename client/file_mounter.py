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
import time
import subprocess

PY2 = sys.version_info[0] == 2

class FileMounter(object):
	def __init__(self, letter):
		self.letter = letter

	def unmount(self):
		# Unmount any mounted games using Virtual Clone Drive
		print("Unmounting any games ...")
		mount_command = '"C:/Program Files (x86)/Elaborate Bytes/VirtualCloneDrive/VCDMount.exe" /u'
		mount_proc = subprocess.Popen(mount_command, stdout=subprocess.PIPE)
		output = mount_proc.stdout.read()
		if not PY2:
			output = output.decode(encoding='UTF-8')

		# Wait till everything is unmounted
		while True:
			print("Waiting for disk unmount ...")
			if os.system("vol {0}: 2>nul>nul".format(self.letter)) == 1:
				break
			time.sleep(1)

	def mount(self, file_name):
		# Mount the game using Virtual Clone Drive
		mount_command = '"C:/Program Files (x86)/Elaborate Bytes/VirtualCloneDrive/VCDMount.exe" \c "' + file_name + '"'
		mount_proc = subprocess.Popen(mount_command, stdout=subprocess.PIPE)
		output = mount_proc.stdout.read()
		if not PY2:
			output = output.decode(encoding='UTF-8')

		# Wait till the game is actually mounted
		while True:
			print("Waiting for disk to mount ...")
			if os.system("vol {0}: 2>nul>nul".format(self.letter)) == 0:
				break
			time.sleep(1)

