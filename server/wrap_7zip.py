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
import subprocess


class Wrap7zip(object):
	def __init__(self):
		# Check if 7zip is installed
		if os.path.isfile('C:/Program Files/7-Zip/7z.exe'):
			self.exe = 'C:/Program Files/7-Zip/7z.exe'
		elif os.path.isfile('C:/Program Files (x86)/7-Zip/7z.exe'):
			self.exe = 'C:/Program Files (x86)/7-Zip/7z.exe'
		else:
			print('7-Zip wrapper could not locate 7z.exe')
			sys.exit()

	def uncompress(self, comprerssed_file, out_dir):
		command = '"{0}" x -y "{1}" -o{2}'.format(self.exe, comprerssed_file, out_dir)
		proc = subprocess.Popen(command, stdout=subprocess.PIPE)
		out, err = proc.communicate()






