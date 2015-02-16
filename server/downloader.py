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
import stat
import threading

PY2 = sys.version_info[0] == 2

if PY2:
	from urllib2 import urlopen
else:
	from urllib.request import urlopen


class Downloader(threading.Thread):
	def __init__(self, url, file_name, dir_name):
		super(Downloader, self).__init__()

		self.url = url
		self.file_name = file_name
		self.dir_name = dir_name
		self.is_success = False
		self.message = None

	def run(self):
		# Get the file name for script
		full_file_name = os.path.join(self.dir_name, self.file_name)

		# Download the file and call the cb after each chunk
		self._download_file(self.url, full_file_name)

		# Make the file executable
		os.chmod(full_file_name, 0o775 | stat.S_IXOTH)

	def _download_file(self, url, file_name):
		CHUNK_SIZE = 1024

		try:
			# Connect with HTTP
			response = urlopen(url)
			if response.code != 200:
				self.is_success = False
				self.message = 'Download failed. Exiting ...'
				sys.exit(1)

			# Read the HTTP header
			content_length = int(response.headers['Content-Length'])
			data = b''
			data_length = 0

			# Read the HTTP body
			while True:
				chunk = response.read(CHUNK_SIZE)
				if not chunk:
					break

				data += chunk
				data_length += len(chunk)
				percent = round((float(data_length) / content_length)*100, 2)

				self._cb_dl_progress(file_name, chunk, data_length, CHUNK_SIZE, content_length, percent)
		except Exception as e:
			self.is_success = False
			self.message = 'Download failed. Exiting ...\n{0}\n{1}'.format(str(e), self.url)
			sys.exit(1)

		# Write the file to disk
		self._cb_dl_done(file_name, data)

	def _cb_dl_progress(self, file_name, chunk, data_length, chunk_size, content_length, percent):
		pass

	def _cb_dl_done(self, file_name, data):
		# Save the file
		with open(file_name, 'wb') as f:
			f.write(data)

		self.is_success = True
		self.message = '    {0}'.format(file_name)


