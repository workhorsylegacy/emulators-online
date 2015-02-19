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

"""
TODO:
. Add searching by publisher, year, and console
. How do we deal with games that use multiple disks in the UI?
. Give an option to upload a binary too
. Have Virtual Clone Drive not popup the mounted directory
. Memory card configs
. Move the mouse cursor to the bottom right corner on start
. Figure out how to hide the emulators and mirror their screen
	onto our own screen.
"""

import os, sys

if sys.version_info[0] == 3:
	print("Python 3 is not yet supported. Use python 2.x instead.")
	sys.exit()

import shutil
import json
import base64
import subprocess

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template

from fuzzywuzzy import fuzz
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

runner = None
demul = demul.Demul()
dolphin = dolphin.Dolphin()
ssf = ssf.SSF()
mupen64plus = mupen64plus.Mupen64Plus()
pcsxr = pcsxr.PCSXR()


def make_db(file_name, path_prefix, binaries_path):
	db = {}

	primary_binary_entensions = [
		'.gdi',
		'.cdi',
		'.iso',
		'.mdf',
		'.z64',
		'.n64',
		'.img',
		'.gcm'
	]

	secondary_binary_entensions = [
		'.raw',
		'.bin'
	]

	for game_name in os.listdir(path_prefix):
		game_path = '{0}/{1}/'.format(path_prefix, game_name)

		if not os.path.isdir(game_path):
			continue
		'''
		# Get the game binary
		binary = None
		for entry in os.listdir(game_path):
			binary_lower = entry.lower()
			if os.path.splitext(binary_lower)[1] in binary_entensions:
				binary = entry
				break
		'''
		# Get the meta data
		meta_data = {}
		meta_file = '{0}{1}'.format(game_path, 'info.json')
		if os.path.isfile(meta_file):
			with open(meta_file, 'rb') as f:
				meta_data = json.load(f)

		# Get the images
		images = []
		for entry in os.listdir(game_path):
			if entry.lower().endswith('.png'):
				images.append(entry)

		db[game_name] = {
			'path' : '{0}/{1}/'.format(path_prefix, game_name),
			'binaries' : [],
			'bios' : '',
			'images' : images,
			'developer' : meta_data.get('developer', ''),
			'genre' : meta_data.get('genre', ''),
		}

	# Get the binaries
	for root, dir, files in os.walk(binaries_path):
		# Sort the files to have primary extensions first
		primary_files = []
		secondary_files = []
		for entry in files:
			full_entry = os.path.join(root, entry)

			# Skip if not a file
			if not os.path.isfile(full_entry):
				continue

			# Skip if a bios file
			if 'bios' in full_entry.lower():
				continue

			# Sort into primary and secondary files
			if os.path.splitext(entry)[1].lower() in primary_binary_entensions:
				primary_files.append(entry)
			elif os.path.splitext(entry)[1].lower() in secondary_binary_entensions:
				secondary_files.append(entry)

		# Only search the secondary files if there are no primary files
		ignore_secondary = False
		if primary_files and secondary_files:
			ignore_secondary = True

		# Get the primary and secondary files if needed
		files = []
		files += primary_files
		if not ignore_secondary:
			files += secondary_files

		for entry in files:
			full_entry = os.path.join(root, entry)

			binary_name = os.path.splitext(entry)[0]
			best_ratio = 0
			best_name = None
			for game_name, data in db.items():
				ratio = fuzz.partial_ratio(game_name, binary_name)
				if ratio > best_ratio:
					best_ratio = ratio
					best_name = game_name
			db[best_name]['binaries'].append(full_entry)
			#print(best_ratio, best_name, binary_name)

	# Write the db to file
	with open('db/{0}'.format(file_name), 'wb') as f:
		f.write(json.dumps(db, sort_keys=True, indent=4, separators=(',', ': ')))


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
		self.write_message(data)

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

		# Unknown message from the client
		else:
			self.log("Unknown action from client: {0}".format(data['action']))

	def _get_db(self, data):
		db = {}

		with open('db/saturn.json', 'rb') as f:
			db['Saturn'] = json.loads(f.read())
		with open('db/playstation.json', 'rb') as f:
			db['Playstation'] = json.loads(f.read())
		with open('db/playstation2.json', 'rb') as f:
			db['Playstation2'] = json.loads(f.read())
		with open('db/gamecube.json', 'rb') as f:
			db['GameCube'] = json.loads(f.read())
		with open('db/nintendo64.json', 'rb') as f:
			db['Nintendo64'] = json.loads(f.read())
		with open('db/dreamcast.json', 'rb') as f:
			db['Dreamcast'] = json.loads(f.read())

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
			demul.run(data['path'], data['binary'])
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

		# Generate the database of games
		#make_db('gamecube.json', 'games/Nintendo/GameCube')
		#make_db('nintendo64.json', 'games/Nintendo/Nintendo64')
		#make_db('saturn.json', 'games/Sega/Saturn')
		make_db('dreamcast.json', 'games/Sega/Dreamcast', 'C:/Users/matt/Desktop/dc')
		#make_db('playstation.json', 'games/Sony/Playstation')
		#make_db('playstation2.json', 'games/Sony/Playstation2')

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



