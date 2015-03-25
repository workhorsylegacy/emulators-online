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
from identify_dreamcast_games import *


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
			'config', 'db', 'downloads',
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

	# Make the html, css, and js files
	files = ['configure.html', 'index.html', 'static/default.css', 
			'static/emu_archive.js', 'static/file_uploader.js',
			'static/input.js', 'static/web_socket.js',
			'static/jquery-2.1.3.min.js', 'static/favicon.ico']

	for file in files:
		if not os.path.isfile(file):
			with open(file, 'wb') as f:
				data = static_files.static_files[file]
				data = base64.b64decode(data)
				f.write(data)

long_running_tasks = {}
runner = None
demul = demul.Demul()
dolphin = dolphin.Dolphin()
ssf = ssf.SSF()
mupen64plus = mupen64plus.Mupen64Plus()
pcsxr = pcsxr.PCSXR()

# Load the game database
db = {}
if os.path.isfile("db/game_db.json"):
	with open("db/game_db.json", 'rb') as f:
		db = json.loads(f.read())

	# Remove any non existent files
	for console, console_data in db.items():
		for name in console_data.keys():
			data = console_data[name]
			if not os.path.isfile(data['binary']):
				console_data.pop(name)

# Load the file modify dates
file_modify_dates = {}
if os.path.isfile("db/file_modify_dates.json"):
	with open("db/file_modify_dates.json", 'rb') as f:
		file_modify_dates = json.loads(f.read())

	# Remove any non existent files from the modify db
	for entry in file_modify_dates.keys():
		if not os.path.isfile(entry):
			file_modify_dates.pop(entry)

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
			self._set_game_directory(data)

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

		data = {
			'action' : 'long_running_tasks',
			'value' : long_running_tasks.keys()
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
		if data['console'] == 'Dreamcast':
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

		elif data['console'] == 'Saturn':
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
		if data['console'] == 'GameCube':
			dolphin.set_button_map(data['value'])

		elif data['console'] == 'Nintendo64':
			mupen64plus.set_button_map(data['value'])

		elif data['console'] == 'Saturn':
			ssf.set_button_map(data['value'])

		elif data['console'] == 'Dreamcast':
			demul.set_button_map(data['value'])

		elif data['console'] == 'Playstation':
			pcsxr.set_button_map(data['value'])

		elif data['console'] == 'Playstation2':
			pcsx2.set_button_map(data['value'])

	def _get_button_map(self, data):
		value = None

		if data['console'] == 'GameCube':
			value = dolphin.get_button_map()

		elif data['console'] == 'Nintendo64':
			value = mupen64plus.get_button_map()

		elif data['console'] == 'Saturn':
			value = ssf.get_button_map()

		elif data['console'] == 'Dreamcast':
			value = demul.get_button_map()

		elif data['console'] == 'Playstation':
			value = pcsxr.get_button_map()

		elif data['console'] == 'Playstation2':
			value = pcsx2.get_button_map()

		data = {
			'action' : 'get_button_map',
			'value' : value,
			'console' : data['console']
		}
		self.write_data(data)

	def _set_game_directory(self, data):
		global long_running_tasks

		# Just return if already a long running "Searching for Dreamcast games" task
		if self.is_long_running_task("Searching for Dreamcast games"):
			return

		def task(socket, data):
			global db
			global file_modify_dates
			global long_running_tasks

			# Add the thread to the list of long running tasks
			self.add_long_running_task("Searching for Dreamcast games", threading.current_thread())

			directory_name = data['directory_name']
			console = data['console']

			if 'Dreamcast' not in db:
				db['Dreamcast'] = {}

			# Walk through all the directories
			percentage = 0
			path_prefix = 'games/Sega/Dreamcast'
			for root, dirs, files in os.walk(directory_name):
				for file in files:
					# Get the full path
					entry = root + '/' + file
					entry = os.path.abspath(entry).replace('\\', '/')

					self.set_long_running_task_percentage("Searching for Dreamcast games", percentage)
					percentage += 1

					# Skip if the game file has not been modified
					old_modify_date = 0
					if entry in file_modify_dates:
						old_modify_date = file_modify_dates[entry]
					modify_date = os.path.getmtime(entry)
					if modify_date == old_modify_date:
						continue
					else:
						file_modify_dates[entry] = modify_date

					if not os.path.isfile(entry):
						continue

					if not console == 'Dreamcast':
						continue

					if not is_dreamcast_file(entry):
						continue

					info = None
					try:
						info = get_dreamcast_game_info(entry)
					except:
						print("Failed to find info for game '{0}'".format(entry))
						continue
					print('getting game info: {0}'.format(info['title']))
					info['file'] = entry

					# Save the info in the db
					if info:
						title = info['title']
						clean_title = title.replace(': ', ' - ').replace('/', '+')
						db['Dreamcast'][title] = {
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
									db['Dreamcast'][title]['images'].append(image_file)

			with open("db/game_db.json", 'wb') as f:
				f.write(json.dumps(db, indent=4, separators=(',', ': ')))

			with open("db/file_modify_dates.json", 'wb') as f:
				f.write(json.dumps(file_modify_dates, indent=4, separators=(',', ': ')))
			print("Done getting games from directory.")

			self.remove_long_running_task("Searching for Dreamcast games")

		# Run the task in a thread
		thread = threading.Thread(target = task, args = (self, data))
		thread.daemon = True
		thread.start()


	def _play_game(self, data):
		if data['console'] == 'GameCube':
			dolphin.run(data['path'], data['binary'])
			self.log('playing')
			print('Running Dolphin ...')

		elif data['console'] == 'Nintendo64':
			mupen64plus.run(data['path'], data['binary'])
			self.log('playing')
			print('Running Mupen64plus ...')

		elif data['console'] == 'Saturn':
			ssf.run(data['path'], data['binary'], data['bios'])
			self.log('playing')
			print('Running SSF ...')

		elif data['console'] == 'Dreamcast':
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

		elif data['console'] == 'Playstation2':
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
		if data['program'] == '7-Zip':
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
			exist = os.path.exists("emulators/PCSX2/pcsx2.exe")
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
						('Start Server (FIXME: Breaks if already started)', icon, start),
						('Stop Server (FIXME: Does not free the port)', icon, stop),
						('View in Browser', icon, view_in_browser),
						('Emulators', icon,
							(
								('Demul', icon, run_demul),
								('SSF', icon, run_ssf),
								('Dolphin', icon, run_dolphin),
								('Mupen 64 Plus', icon, run_mupen64plus),
								('PSX-Reloaded', icon, run_pcsxr),
								('PCSX2', icon, run_pcsx2),
							)
						)
					)

	tray_icon.TrayIcon(icon, hover_text, menu_options, on_quit=stop, on_start=start, default_menu_index=1)



