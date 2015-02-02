#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2015, Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# This software uses a MIT style license
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

