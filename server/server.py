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

if sys.version_info[0] == 3:
	print("Python 3 is not yet supported. Use python 2.x instead.")
	sys.exit()

import shutil
import json
import base64
import subprocess
import zlib
import threading
import glob

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template

import tray_icon
import downloader
import wrap_7zip
import demul
import ssf
import dolphin
import mupen64plus
import pcsxr
import pcsx2


# Move to the main emu_archive directory no matter what path we are launched from
current_path = os.path.abspath(os.path.dirname(sys.argv[0]))
if current_path.endswith('server'):
	os.chdir(os.path.join(current_path, '..'))

# Figure out if running as an exe
IS_EXE = '__file__' not in globals() and sys.argv[0].endswith('.exe')

# When running as an exe, log to a file
'''
if IS_EXE:
	if os.path.isfile('log.txt'):
		os.remove('log.txt')

	log_file = open('log.txt', 'wb')
	sys.stderr = log_file
	sys.stdout = log_file
'''
# When running as an exe, generate the files
if IS_EXE:
	import static_files

	# Make the directory structure
	dirs = [
			'config', 'cache', 'downloads',
			'emulators', 'server',
			'static', 'games',
			'games/Nintendo/',
			'games/Nintendo/GameCube/',
			'games/Nintendo/Nintendo64/',
			'games/Sega/',
			'games/Sega/Saturn/',
			'games/Sega/Dreamcast/',
			'games/Sony/',
			'games/Sony/Playstation/',
			'games/Sony/Playstation2/'
	]

	for dir in dirs:
		if not os.path.exists(dir):
			os.mkdir(dir)

	# Make the html, css, js, and json files
	files = ['configure.html', 'index.html', 'static/default.css', 
			'static/emu_archive.js', 'static/file_uploader.js',
			'static/input.js', 'static/web_socket.js',
			'static/jquery-2.1.3.min.js', 'static/favicon.ico',
			'db_dreamcast_official_eu.json',
			'db_dreamcast_official_jp.json',
			'db_dreamcast_official_us.json',
			'db_dreamcast_unofficial.json',
			'db_playstation2_official_as.json',
			'db_playstation2_official_au.json',
			'db_playstation2_official_eu.json',
			'db_playstation2_official_jp.json',
			'db_playstation2_official_ko.json',
			'db_playstation2_official_us.json',
			]

	for file in files:
		if not os.path.isfile(file):
			with open(file, 'wb') as f:
				data = static_files.static_files[file]
				data = base64.b64decode(data)
				f.write(data)

from identify_dreamcast_games import *
from identify_playstation2_games import *

long_running_tasks = {}
runner = None
demul = demul.Demul()
dolphin = dolphin.Dolphin()
ssf = ssf.SSF()
mupen64plus = mupen64plus.Mupen64Plus()
pcsxr = pcsxr.PCSXR()

# Load the game database
db = {}
consoles = [
	'gamecube',
	'nintendo64',
	'saturn',
	'dreamcast',
	'playstation1',
	'playstation2',
]
for console in consoles:
	db[console] = {}
	if os.path.isfile("cache/game_db_{0}.json".format(console)):
		with open("cache/game_db_{0}.json".format(console), 'rb') as f:
			db[console] = json.loads(f.read())

		# Remove any non existent files
		for name in db[console].keys():
			data = db[console][name]
			if not os.path.isfile(data['binary']):
				db[console].pop(name)

# Load the file modify dates
file_modify_dates = {}
for console in consoles:
	file_modify_dates[console] = {}
	if os.path.isfile("cache/file_modify_dates_{0}.json".format(console)):
		with open("cache/file_modify_dates_{0}.json".format(console), 'rb') as f:
			file_modify_dates[console] = json.loads(f.read())

		# Remove any non existent files from the modify db
		for entry in file_modify_dates[console].keys():
			if not os.path.isfile(entry):
				file_modify_dates[console].pop(entry)

def clean_path(file_path):
	#file_path = os.path.abspath(file_path)
	file_path = file_path.replace('\\', '/')
	#file_path  = file_path.replace(': ', ' - ').replace('/', '+')
	return file_path

def abs_path(file_path):
	file_path = os.path.abspath(file_path)
	file_path = file_path.replace('\\', '/')
	#file_path  = file_path.replace(': ', ' - ').replace('/', '+')
	return file_path

# FIXME: We should only need one handler for sending html files
class MainHandler(tornado.web.RequestHandler):
	def get(self):
		loader = tornado.template.Loader(".")
		self.write(loader.load("index.html").generate())

class ConfigureHandler(tornado.web.RequestHandler):
	def get(self):
		loader = tornado.template.Loader(".")
		self.write(loader.load("configure.html").generate())

class WebSocketHandler(tornado.websocket.WebSocketHandler):
	# Make it so the same-origin policy is turned off
	# This makes it so it can accept requests from any url
	# http://tornado.readthedocs.org/en/latest/websocket.html
	def check_origin(self, origin):
		return True

	def write_data(self, data):
		data = json.dumps(data)
		try:
			self.write_message(data)
		except tornado.websocket.WebSocketClosedError as err:
			pass

	def log(self, message, echo=False):
		data = {
			'action' : 'log',
			'value' : message
		}
		self.write_data(data)

		if echo:
			print(message)
		
	def open(self):
		self.log('Server starting ...', echo=True)

	def on_close(self):
		print('Server stopping ...')

	def on_message(self, message):
		global runner

		data = json.loads(message)

		# Client wants to play a game
		if data['action'] == 'play':
			self._play_game(data)

		# Client wants to download a file
		elif data['action'] == 'download':
			self._download_file(data)

		# Client wants to know if a file is installed
		elif data['action'] == 'is_installed':
			self._is_installed(data)

		# Client wants to install a program
		elif data['action'] == 'install':
			self._install(data)

		elif data['action'] == 'uninstall':
			self._uninstall(data)

		elif data['action'] == 'set_button_map':
			self._set_button_map(data)

		elif data['action'] == 'get_button_map':
			self._get_button_map(data)

		elif data['action'] == 'set_bios':
			self._set_bios(data)

		elif data['action'] == 'get_db':
			self._get_db(data)

		elif data['action'] == 'set_game_directory':
			from win32gui import GetWindowText, EnumWindows, GetForegroundWindow, GetDesktopWindow
			from win32com.shell import shell, shellcon

			def findWindowWithTitleText(title_text):
				# Get the handles of all the windows
				res = []
				def callback(hwnd, arg):
					res.append(hwnd)
				EnumWindows(callback, 0)

				# Find the window with the desired title bar text
				for hwnd in res:
					text = GetWindowText(hwnd)
					#print(text)
					if title_text in text:
						return(hwnd, text)

				return (None, None)

			# First try checking if Firefox or Chrome is the foreground window
			hwnd = GetForegroundWindow()
			text = GetWindowText(hwnd)

			# If the focused window is not Chrome or Firefox, find them manually
			if ' - Mozilla Firefox' not in text and ' - Google Chrome' not in text:
				# If not, find any Firefox window
				hwnd, text = findWindowWithTitleText(' - Mozilla Firefox')
				if not hwnd or not text:
					# If not, find any Chrome window
					hwnd, text = findWindowWithTitleText(' - Google Chrome')
					if not hwnd or not text:
						# If not, find the Desktop window
						hwnd = GetDesktopWindow()
						text = 'Desktop'
			if not hwnd or not text:
				print("Failed to find any Firefox, Chrome, or Desktop window to put the Folder Dialog on top of.")
				sys.exit(1)

			print(hwnd, text)
			desktop_pidl = shell.SHGetFolderLocation(0, shellcon.CSIDL_DESKTOP, 0, 0)
			pidl, display_name, image_list = shell.SHBrowseForFolder(
				hwnd,
				desktop_pidl,
				"Select a folder search for games",
				0,
				None,
				None
			)
			if pidl:
				print(shell.SHGetPathFromIDList(pidl))
			#self._set_game_directory(data)

		# Unknown message from the client
		else:
			self.log("Unknown action from client: {0}".format(data['action']))

	def is_long_running_task(self, task_name):
		global long_running_tasks

		return task_name in long_running_tasks

	def remove_long_running_task(self, task_name):
		global long_running_tasks

		if task_name in long_running_tasks:
			long_running_tasks.pop(task_name)

		# Make a copy of long_running_tasks without the threads
		copy = {}
		for name, data in long_running_tasks.items():
			copy[name] = data['percentage']

		data = {
			'action' : 'long_running_tasks',
			'value' : copy
		}
		self.write_data(data)

	def add_long_running_task(self, task_name, thread):
		global long_running_tasks

		long_running_tasks[task_name] = {
			'thread' : thread,
			'percentage' : 0,
		}

		# Make a copy of long_running_tasks without the threads
		copy = {}
		for name, data in long_running_tasks.items():
			copy[name] = data['percentage']

		data = {
			'action' : 'long_running_tasks',
			'value' : copy
		}
		self.write_data(data)

	def set_long_running_task_percentage(self, task_name, percentage):
		global long_running_tasks

		long_running_tasks[task_name]['percentage'] = percentage

		# Make a copy of long_running_tasks without the threads
		copy = {}
		for name, data in long_running_tasks.items():
			copy[name] = data['percentage']

		data = {
			'action' : 'long_running_tasks',
			'value' : copy
		}
		self.write_data(data)

	def _get_db(self, data):
		global db

		data = {
			'action' : 'get_db',
			'value' : db
		}
		self.write_data(data)

	def _set_bios(self, data):
		if data['console'] == 'dreamcast':
			if not os.path.isdir('emulators/Demul/roms'):
				os.mkdir('emulators/Demul/roms')

			if data['type'] == 'awbios.zip':
				with open('emulators/Demul/roms/awbios.zip', 'wb') as f:
					f.write(base64.b64decode(data['value']))
			elif data['type'] == 'dc.zip':
				with open('emulators/Demul/roms/dc.zip', 'wb') as f:
					f.write(base64.b64decode(data['value']))
			elif data['type'] == 'naomi.zip':
				with open('emulators/Demul/roms/naomi.zip', 'wb') as f:
					f.write(base64.b64decode(data['value']))
			elif data['type'] == 'naomi2.zip':
				with open('emulators/Demul/roms/naomi2.zip', 'wb') as f:
					f.write(base64.b64decode(data['value']))

		elif data['console'] == 'saturn':
			if not os.path.isdir('emulators/SSF_012_beta_R4/bios'):
				os.mkdir('emulators/SSF_012_beta_R4/bios')

			if data['type'] == 'USA':
				with open('emulators/SSF_012_beta_R4/bios/Sega Saturn BIOS (US).bin', 'wb') as f:
					f.write(base64.b64decode(data['value']))
			elif data['type'] == 'EUR':
				with open('emulators/SSF_012_beta_R4/bios/Sega Saturn BIOS (EUR).bin', 'wb') as f:
					f.write(base64.b64decode(data['value']))
			elif data['type'] == 'JAP':
				with open('emulators/SSF_012_beta_R4/bios/Sega Saturn BIOS (JAP).bin', 'wb') as f:
					f.write(base64.b64decode(data['value']))


	def _set_button_map(self, data):
		if data['console'] == 'gamecube':
			dolphin.set_button_map(data['value'])

		elif data['console'] == 'nintendo64':
			mupen64plus.set_button_map(data['value'])

		elif data['console'] == 'saturn':
			ssf.set_button_map(data['value'])

		elif data['console'] == 'dreamcast':
			demul.set_button_map(data['value'])

		elif data['console'] == 'Playstation':
			pcsxr.set_button_map(data['value'])

		elif data['console'] == 'playstation2':
			pcsx2.set_button_map(data['value'])

	def _get_button_map(self, data):
		value = None

		if data['console'] == 'gamecube':
			value = dolphin.get_button_map()

		elif data['console'] == 'nintendo64':
			value = mupen64plus.get_button_map()

		elif data['console'] == 'saturn':
			value = ssf.get_button_map()

		elif data['console'] == 'dreamcast':
			value = demul.get_button_map()

		elif data['console'] == 'Playstation':
			value = pcsxr.get_button_map()

		elif data['console'] == 'playstation2':
			value = pcsx2.get_button_map()

		data = {
			'action' : 'get_button_map',
			'value' : value,
			'console' : data['console']
		}
		self.write_data(data)

	def _set_game_directory(self, data):

		# Just return if already a long running "Searching for dreamcast games" task
		if self.is_long_running_task("Searching for {0} games".format(data['console'])):
			return

		def task(socket, data):
			global db
			global file_modify_dates

			directory_name = data['directory_name']
			console = data['console']

			# Add the thread to the list of long running tasks
			self.add_long_running_task("Searching for {0} games".format(console), threading.current_thread())

			# Get the total number of files
			total_files = 0.0
			path_prefix = None
			if console == 'gamecube':
				path_prefix = 'games/Nintendo/GameCube'
			elif console == 'nintendo64':
				path_prefix = 'games/Nintendo/Nintendo64'
			elif console == 'saturn':
				path_prefix = 'games/Sega/Saturn'
			elif console == 'dreamcast':
				path_prefix = 'games/Sega/Dreamcast'
			elif console == 'playstation1':
				path_prefix = 'games/Sony/Playstation1'
			elif console == 'playstation2':
				path_prefix = 'games/Sony/Playstation2'

			for root, dirs, files in os.walk(directory_name):
				for file in files:
					total_files += 1

			# Walk through all the directories
			done_files = 0.0
			for root, dirs, files in os.walk(directory_name):
				for file in files:
					# Get the full path
					entry = root + '/' + file
					entry = os.path.abspath(entry).replace('\\', '/')

					# Get the percentage of the progress looping through files
					percentage = (done_files / total_files) * 100.0
					self.set_long_running_task_percentage("Searching for {0} games".format(console), percentage)
					done_files += 1

					# Skip if the the entry is not a file
					if not os.path.isfile(entry):
						continue

					# Skip if the game file has not been modified
					old_modify_date = 0
					if entry in file_modify_dates[console]:
						old_modify_date = file_modify_dates[console][entry]
					modify_date = os.path.getmtime(entry)
					if modify_date == old_modify_date:
						continue
					else:
						file_modify_dates[console][entry] = modify_date

					# Skip if the file is not the right kind for this console
					if console == 'dreamcast':
						if not is_dreamcast_file(entry):
							continue
					elif console == 'playstation2':
						if not is_playstation2_file(entry):
							continue
					else:
						raise Exception("Unexpected console: {0}".format(console))

					# Get the game info
					info = None
					try:
						if console == 'dreamcast':
							info = get_dreamcast_game_info(entry)
						elif console == 'playstation2':
							info = get_playstation2_game_info(entry)
						else:
							raise Exception("Unexpected console: {0}".format(console))
					except:
						print("Failed to find info for game '{0}'".format(entry))
						continue
					print('getting game info: {0}'.format(info['title']))
					info['file'] = entry

					# Save the info in the db
					if info:
						title = info['title']
						clean_title = title.replace(': ', ' - ').replace('/', '+')
						db[console][title] = {
							'path' : clean_path('{0}/{1}/'.format(path_prefix, clean_title)),
							'binary' : abs_path(info['file']),
							'bios' : '',
							'images' : [],
							'developer' : info.get('developer', ''),
							'genre' : info.get('genre', ''),
						}

						# Get the images
						image_dir = path_prefix + '/' + title + '/'
						for img in ['title_big.png', 'title_small.png']:
							if os.path.isdir(image_dir):
								image_file = image_dir + img
								if os.path.isfile(image_file):
									db[console][title]['images'].append(image_file)

			with open("cache/game_db_{0}.json".format(console), 'wb') as f:
				f.write(json.dumps(db[console], indent=4, separators=(',', ': ')))

			with open("cache/file_modify_dates_{0}.json".format(console), 'wb') as f:
				f.write(json.dumps(file_modify_dates[console], indent=4, separators=(',', ': ')))
			print("Done getting games from directory.")

			self.remove_long_running_task("Searching for {0} games".format(console))

		# Run the task in a thread
		thread = threading.Thread(target = task, args = (self, data))
		thread.daemon = True
		thread.start()


	def _play_game(self, data):
		if data['console'] == 'gamecube':
			dolphin.run(data['path'], data['binary'])
			self.log('playing')
			print('Running Dolphin ...')

		elif data['console'] == 'nintendo64':
			mupen64plus.run(data['path'], data['binary'])
			self.log('playing')
			print('Running Mupen64plus ...')

		elif data['console'] == 'saturn':
			ssf.run(data['path'], data['binary'], data['bios'])
			self.log('playing')
			print('Running SSF ...')

		elif data['console'] == 'dreamcast':
			def save_memory_card_cb(memory_card):
				memory_card = zlib.compress(memory_card, 9)
				# FIXME: Send the memory card to the server
				print("FIXME: Memory card needs saving length {0}".format(len(memory_card)))

			demul.run(data['path'], data['binary'], on_stop = save_memory_card_cb)
			self.log('playing')
			print('Running Demul ...')

		elif data['console'] == 'Playstation':
			pcsxr.run(data['path'], data['binary'])
			self.log('playing')
			print('Running PCSX-Reloaded ...')

		elif data['console'] == 'playstation2':
			pcsx2.run(data['path'], data['binary'])
			self.log('playing')
			print('Running PCSX2 ...')

	def _download_file(self, data):
		def progress_cb(name, server, progress):
			data = {
				'action' : 'progress',
				'value' : progress,
				'name' : name
			}
			server.write_data(data)

		t = EmuDownloader(self, progress_cb, data['name'], data['url'], data['file'], data['dir'])
		t.daemon = True
		t.start()
		t.join()
		if not t.is_success:
			print(t.message)
			sys.exit(1)

	def _install(self, data):
		# Start uncompressing
		message = {
			'action' : 'uncompress',
			'is_start' : True,
			'name' : data['file']
		}
		self.write_data(message)

		if data['file'] == 'SetupVirtualCloneDrive.exe':
			os.chdir(data['dir'])
			proc = subprocess.Popen([data['file'], '/S'], stdout=subprocess.PIPE, shell=True) # Silent install
			proc.communicate()
			os.chdir('..')
		elif data['file'] == '7z920.exe':
			os.chdir(data['dir'])
			proc = subprocess.Popen([data['file'], '/S'], stdout=subprocess.PIPE, shell=True) # Silent install
			proc.communicate()
			os.chdir('..')
		elif data['file'] == 'nullDC_104_r136.7z':
			wrap = wrap_7zip.Wrap7zip()
			wrap.uncompress(os.path.join(data['dir'], 'nullDC_104_r136.7z'), 'emulators/NullDC')
		elif data['file'] == 'demul0582.rar':
			wrap = wrap_7zip.Wrap7zip()
			wrap.uncompress(os.path.join(data['dir'], 'demul0582.rar'), 'emulators/Demul')
		elif data['file'] == 'SSF_012_beta_R4.zip':
			wrap = wrap_7zip.Wrap7zip()
			wrap.uncompress(os.path.join(data['dir'], 'SSF_012_beta_R4.zip'), 'emulators')
		elif data['file'] == 'dolphin-master-4.0-5363-x64.7z':
			wrap = wrap_7zip.Wrap7zip()
			wrap.uncompress(os.path.join(data['dir'], 'dolphin-master-4.0-5363-x64.7z'), 'emulators')
		elif data['file'] == 'mupen64plus-bundle-win32-2.0.zip':
			wrap = wrap_7zip.Wrap7zip()
			wrap.uncompress(os.path.join(data['dir'], 'mupen64plus-bundle-win32-2.0.zip'), 'emulators/Mupen64Plus')
		elif data['file'] == 'pcsxr-1.9.93-win32.zip':
			wrap = wrap_7zip.Wrap7zip()
			wrap.uncompress(os.path.join(data['dir'], 'pcsxr-1.9.93-win32.zip'), 'emulators')
		elif data['file'] == 'pcsx2-v1.3.1-8-gf88bea5-windows-x86.7z':
			wrap = wrap_7zip.Wrap7zip()
			wrap.uncompress(os.path.join(data['dir'], 'pcsx2-v1.3.1-8-gf88bea5-windows-x86.7z'), 'emulators')

		# End uncompressing
		message = {
			'action' : 'uncompress',
			'is_start' : False,
			'name' : data['file']
		}
		self.write_data(message)

	def _uninstall(self, data):
		if data['program'] == 'VirtualCloneDrive':
			pass
		elif data['program'] == 'NullDC':
			shutil.rmtree('emulators/NullDC')
		elif data['program'] == 'Demul':
			shutil.rmtree('emulators/Demul')
		elif data['program'] == 'SSF':
			shutil.rmtree('emulators/SSF_012_beta_R4')
		elif data['program'] == 'Dolphin':
			shutil.rmtree('emulators/Dolphin-x64')
		elif data['program'] == 'Mupen64Plus':
			shutil.rmtree('emulators/Mupen64Plus')
		elif data['program'] == 'PCSX-Reloaded':
			shutil.rmtree('emulators/pcsxr')
		elif data['program'] == 'PCSX2':
			shutil.rmtree('emulators/pcsx2')

	def _is_installed(self, data):
		if data['program'] == 'DirectX End User Runtime':
			# Paths on Windows 8.1 X86_32 and X86_64
			exist = (len(glob.glob("C:/Windows/SysWOW64/d3dx10_*.dll")) > 0 or \
					len(glob.glob("C:/Windows/System32/d3dx11_*.dll")) > 0) and \
					(len(glob.glob("C:/Windows/SysWOW64/d3dx11_*.dll")) > 0 or \
					len(glob.glob("C:/Windows/System32/d3dx10_*.dll")) > 0)
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : 'DirectX End User Runtime'
			}
			self.write_data(data)
		elif data['program'] == 'Visual C++ 2010 redist': # msvcr100.dll
			# Paths on Windows 8.1 X86_32 and X86_64
			exist = os.path.exists("C:/Windows/SysWOW64/msvcr100.dll") or \
					os.path.exists("C:/Windows/System32/msvcr100.dll")
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : 'Visual C++ 2010 redist'
			}
			self.write_data(data)
		elif data['program'] == 'Visual C++ 2013 redist': # msvcr120.dll
			# Paths on Windows 8.1 X86_32 and X86_64
			exist = os.path.exists("C:/Windows/SysWOW64/msvcr120.dll") or \
					os.path.exists("C:/Windows/System32/msvcr120.dll")
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : 'Visual C++ 2013 redist'
			}
			self.write_data(data)
		elif data['program'] == '7-Zip':
			exist = os.path.exists("C:/Program Files/7-Zip/7z.exe") or \
					os.path.exists("C:/Program Files (x86)/7-Zip/7z.exe")
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : '7-Zip'
			}
			self.write_data(data)
		elif data['program'] == 'VirtualCloneDrive':
			exist = os.path.exists("C:/Program Files (x86)/Elaborate Bytes/VirtualCloneDrive/VCDMount.exe")
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : 'VirtualCloneDrive'
			}
			self.write_data(data)
		elif data['program'] == 'NullDC':
			exist = os.path.exists("emulators/NullDC/nullDC_Win32_Release-NoTrace.exe")
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : 'NullDC'
			}
			self.write_data(data)
		elif data['program'] == 'Demul':
			exist = os.path.exists("emulators/Demul/demul.exe")
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : 'Demul'
			}
			self.write_data(data)
		elif data['program'] == 'SSF':
			exist = os.path.exists("emulators/SSF_012_beta_R4/SSF.exe")
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : 'SSF'
			}
			self.write_data(data)
		elif data['program'] == 'Dolphin':
			exist = os.path.exists("emulators/Dolphin-x64/Dolphin.exe")
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : 'Dolphin'
			}
			self.write_data(data)
		elif data['program'] == 'PCSX-Reloaded':
			exist = os.path.exists("emulators/pcsxr/pcsxr.exe")
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : 'PCSX-Reloaded'
			}
			self.write_data(data)
		elif data['program'] == 'PCSX2':
			exist = os.path.exists("emulators/pcsx2/pcsx2.exe")
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : 'PCSX2'
			}
			self.write_data(data)
		elif data['program'] == 'Mupen 64 Plus':
			exist = os.path.exists("emulators/Mupen64Plus/mupen64plus.exe")
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : 'Mupen 64 Plus'
			}
			self.write_data(data)
		else:
			print('Unknown program to check if installed: {0}'.format(data['program']))


class EmuDownloader(downloader.Downloader):
	def __init__(self, server, progress_cb, name, url, file_name, dir_name):
		super(EmuDownloader, self).__init__(url, file_name, dir_name)
		self.server = server
		self.progress_cb = progress_cb
		self.name = name

	def _cb_dl_progress(self, file_name, chunk, data_length, chunk_size, content_length, percent):
		self.progress_cb(self.name, self.server, percent)


if __name__ == '__main__':
	icon = 'static/favicon.ico'
	hover_text = "Emu Archive"
	server = None
	port = 8080
	ws_port = 9090
	server_thread = None

	def start(trayIcon):
		import threading

		def start_server(port, ws_port):
			global server

			application = tornado.web.Application([
				(r'/', MainHandler),
				(r'/index.html', MainHandler),
				(r'/configure.html', ConfigureHandler),
				(r"/(.*)", tornado.web.StaticFileHandler, {"path" : r"./"}),
			])

			application.listen(port)
			print('HTTP server running on http://localhost:{0} ...'.format(port))

			ws_application = tornado.web.Application([
				(r'/ws', WebSocketHandler),
			])

			ws_application.listen(ws_port)
			print('WebSocket server running on ws://localhost:{0}/ws ...'.format(ws_port))

			server = tornado.ioloop.IOLoop.instance()
			server.start()

		# Start the server in its own thread
		server_thread = threading.Thread(target=start_server, args = (port, ws_port))
		server_thread.start()

	# FIXME: This does not free the port
	def stop(trayIcon):
		global server

		if server:
			server.stop()
		server = None
		tornado.ioloop.IOLoop.instance().stop()
		print('Server exiting ...')

	def view_in_browser(trayIcon):
		import webbrowser
		webbrowser.open_new('http://localhost:{0}'.format(port))

	def run_demul(trayIcon):
		if demul.is_installed():
			demul.run(None, None)
			print('Running Demul ...')
		else:
			print('Demul is not installed')

	def run_ssf(trayIcon):
		if ssf.is_installed():
			ssf.run(None, None, None)
			print('Running SSF ...')
		else:
			print('SSF is not installed')

	def run_dolphin(trayIcon):
		if dolphin.is_installed():
			dolphin.run(None, None)
			print('Running Dolphin ...')
		else:
			print('Dolphin is not installed')

	def run_mupen64plus(trayIcon):
		print("Can't run Mupen64Plus without a game")

	def run_pcsxr(trayIcon):
		if pcsxr.is_installed():
			pcsxr.run(None, None)
			print('Running PCSX-Reloaded ...')
		else:
			print('PCSX-Reloaded is not installed')

	def run_pcsx2(trayIcon):
		print("FIXME")

	if IS_EXE:
		view_in_browser(None)

	menu_options = (
						#('Start Server (FIXME: Breaks if already started)', icon, start),
						#('Stop Server (FIXME: Does not free the port)', icon, stop),
						('View in Browser', icon, view_in_browser),
						('Emulators', icon,
							(
								('Demul', icon, run_demul),
								#('SSF', icon, run_ssf),
								#('Dolphin', icon, run_dolphin),
								#('Mupen 64 Plus', icon, run_mupen64plus),
								#('PSX-Reloaded', icon, run_pcsxr),
								#('PCSX2', icon, run_pcsx2),
							)
						)
					)

	tray_icon.TrayIcon(icon, hover_text, menu_options, on_quit=stop, on_start=start, default_menu_index=1)



