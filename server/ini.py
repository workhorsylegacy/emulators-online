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


import os


def read_ini_file(file_path):
	with open(file_path, 'r') as f:
		ini_data = f.read()

	config = {}

	# Read the ini file into a dictionary
	header = None
	for line in ini_data.splitlines():
		# Line is a header
		if '[' in line and ']' in line:
			header = line.split('[')[1].split(']')[0]
			config[header] = {}
			#print(header)
		# Line is a key value pair
		elif ' = ' in line:
			key, value = line.split(' = ')
			config[header][key] = value
			#print('    {0} = {1}'.format(key, value))

	return config


def write_ini_file(file_name, config):
	with open(file_name, 'w') as f:
		for header, pairs in config.items():
			# Header
			f.write('[{0}]\r\n'.format(header))

			# Keys and values
			for key, value in pairs.items():
				f.write('{0} = {1}\r\n'.format(key, value))

			# Two spaces at the end of a section
			f.write('\r\n\r\n')

