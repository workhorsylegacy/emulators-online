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
import json


class BaseConsole(object):
	def __init__(self, config_path):
		self.config_path = config_path
		self.button_map = {}

		# Load the config
		if os.path.isfile(self.config_path):
			with open(self.config_path, 'r') as f:
				self.button_map = json.loads(f.read())

	def set_button_map(self, button_map):
		self.button_map = button_map
		
		# Save the config
		with open(self.config_path, 'w') as f:
			f.write(json.dumps(self.button_map, sort_keys=True, indent=4, separators=(',', ': ')))

	def get_button_map(self):
		return self.button_map

	def goodJoin(self, path_a, path_b):
		path = path_a + path_b
		path = os.path.abspath(path)
		path = path.replace("\\", "/")
		return path

