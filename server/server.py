#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2015, Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# Py-osinfo is a Python module to get the OS type, brand, release, and kernel
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
. Have it auto download Virtual Clone Drive for emulators that need it
. Have it auto download and config emulators
. Controller configs
. Memory configs
. Move the mouse cursor to the bottom left corner on start
"""

import os, sys
import json
import subprocess

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template

import tray_icon
import file_mounter
import downloader
import emu_runner

PY2 = sys.version_info[0] == 2

if PY2:
	import ConfigParser as configparser
else:
	import configparser

# Move to the main emu_archive directory no matter what path we are launched from
current_path = os.path.abspath(os.path.dirname(sys.argv[0]))
if current_path.endswith('server'):
	os.chdir(os.path.join(current_path, '..'))

runner = None

def read_ini_file(file_path):
	with open(file_path, 'rb') as f:
		ini_data = f.read()

	# Read the ini file into a dictionary
	bios_path = os.path.abspath('emulators/demul0582/roms/')
	sections = ini_data.split('\r\n\r\n\r\n')
	config = {}
	header = None
	for section in sections:
		for line in section.split('\r\n'):
			if '[' in line and ']' in line:
				header = line.split('[')[1].split(']')[0]
				config[header] = {}
				#print(header)
			elif ' = ' in line:
				key, value = line.split(' = ')
				config[header][key] = value
				#print('    {0} = {1}'.format(key, value))
			else:
				break

	return config


def write_ini_file(file_name, config):
	with open(file_name, 'wb') as f:
		for header, pairs in config.items():
			# Header
			f.write('[{0}]\r\n'.format(header))

			# Keys and values
			for key, value in pairs.items():
				f.write('{0} = {1}\r\n'.format(key, value))

			# Two spaces at the end of a section
			f.write('\r\n\r\n')


def make_db(file_name, path_prefix):
	db = {}

	for game_name in os.listdir(path_prefix):
		game_path = '{0}/{1}/'.format(path_prefix, game_name)

		if not os.path.isdir(game_path):
			continue

		binary_entensions = [
			'.bin',
			'.mdf',
			'.iso',
			'.z64',
			'.cdi',
			'.gdi',
			'.n64',
			'.img',
			'.gcm'
		]

		# Get the game binary
		binary = None
		for entry in os.listdir(game_path):
			binary_lower = entry.lower()
			if os.path.splitext(binary_lower)[1] in binary_entensions:
				binary = entry
				break

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
			'binary' : binary,
			'bios' : '',
			'images' : images,
			'developer' : meta_data.get('developer', ''),
			'genre' : meta_data.get('genre', ''),
		}

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

def goodJoin(path_a, path_b):
	path = path_a + path_b
	path = os.path.abspath(path)
	path = path.replace("\\", "/")
	return path

class WebSocketHandler(tornado.websocket.WebSocketHandler):
	def write_data(self, data):
		data = json.dumps(data)
		self.write_message(data)

	def open(self):
		data = {
			'action' : 'log',
			'value' : 'Server starting ...'
		}
		self.write_data(data)
		print('Server starting ...')

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

		# Unknown message from the client
		else:
			data = {
				'action' : 'log',
				'value' : "Unknown action from client: {0}".format(data['action'])
			}
			self.write_data(data)
			print('received:', message)

	def _play_game(self, data):
		if data['console'] == 'GameCube':
			# Read the config file if it exist
			ini_path = os.path.expanduser('~/Documents/Dolphin Emulator/Config/Dolphin.ini')
			if os.path.isfile(ini_path):
				config = configparser.ConfigParser()
				config.optionxform = str
				config.read(ini_path)

				# Render to the main window
				config.set('Display', 'RenderToMain', 'True')

				# Stop popup error dialogs
				config.set('Interface', 'UsePanicHandlers', 'False')

				# Save changes
				with open(ini_path, 'w') as f:
					config.write(f)

			# Run the game
			os.chdir("emulators/Dolphin-x64/")
			game_path = goodJoin("../../", data['path'] + '/' + data['binary'])
			command = '"Dolphin.exe" --batch --exec="' + game_path + '"'
			runner = emu_runner.EmuRunner(command, 'Dolphin 4.0', full_screen_alt_enter=True)
			runner.run()
			os.chdir("../..")

			data = {
				'action' : 'log',
				'value' : 'playing'
			}
			self.write_data(data)
			print('Running Dolphin ...')

		elif data['console'] == 'Nintendo64':
			# Run the game
			os.chdir("emulators/mupen64plus-bundle-win32-2.0/")
			game_path = goodJoin("../../", data['path'] + '/' + data['binary'])
			command = '"Mupen64plus.exe" --fullscreen "' + game_path + '"'
			runner = emu_runner.EmuRunner(command, 'Mupen64Plus', full_screen_alt_enter=False)
			runner.run()
			os.chdir("../..")
			data = {
				'action' : 'log',
				'value' : 'playing'
			}
			self.write_data(data)
			print('Running Mupen64plus ...')

		elif data['console'] == 'Saturn':
			# Mount the game
			mounter = file_mounter.FileMounter("D")
			mounter.unmount()
			mounter.mount(data['path'] + '/' + data['binary'])

			# Get the bios path
			bios_path = data['bios']
			if bios_path:
				bios_path = os.path.abspath('emulators/SSF_012_beta_R4/bios/' + bios_path)

			# SSF setup via INI file
			config = configparser.ConfigParser()
			config.optionxform = str
			config.read("emulators/SSF_012_beta_R4/SSF.ini")

			# Bios
			config.set("Peripheral", "SaturnBIOS", '"' + bios_path + '"')

			# Full Screen
			config.set("Other", "ScreenMode", '"0"')

			# Save changes
			with open('emulators/SSF_012_beta_R4/SSF.ini', 'w') as f:
				config.write(f)

			# Run the game
			os.chdir("emulators/SSF_012_beta_R4/")
			game_path = goodJoin("../../", data['path'] + '/' + data['binary'])
			command = '"SSF.exe" "' + game_path + '"'
			runner = emu_runner.EmuRunner(command, 'SSF', full_screen_alt_enter=True)
			runner.run()
			os.chdir("../..")
			data = {
				'action' : 'log',
				'value' : 'playing'
			}
			self.write_data(data)
			print('Running SSF ...')

		elif data['console'] == 'Dreamcast':
			# FIXME: We have to parse the ini file by hand because ConfigParser cannot read unicode
			config = read_ini_file('emulators/demul0582/Demul.ini')

			# Bios
			bios_path = os.path.abspath('emulators/demul0582/roms/')
			config['files']['roms0'] = bios_path
			config['files']['romsPathsCount'] = '1'

			# Plugins
			plugins_path = os.path.abspath('emulators/demul0582/plugins/')
			config['plugins']['directory'] = plugins_path

			# nvram
			nvram_path = os.path.abspath('emulators/demul0582/nvram/')
			config['files']['nvram'] = nvram_path

			# Get the DirectX version
			directx_dll = config['plugins']['gpu']
			directx_version = None
			if directx_dll == 'gpuDX11.dll':
				directx_version = 'gpuDX11hw'
			elif directx_dll == 'gpuDX10.dll':
				directx_version = 'gpuDX10hw'

			# Save the ini file
			write_ini_file('emulators/demul0582/Demul.ini', config)

			# Run the game
			os.chdir("emulators/demul0582/")
			game_path = goodJoin("../../", data['path'] + '/' + data['binary'])
			command = '"demul.exe" -run=dc -image="' + game_path + '"'
			runner = emu_runner.EmuRunner(command, directx_version, full_screen_alt_enter=True)
			runner.run()
			os.chdir("../..")
			data = {
				'action' : 'log',
				'value' : 'playing'
			}
			self.write_data(data)
			print('Running Demul ...')

		elif data['console'] == 'Playstation':
			# Run the game
			os.chdir("emulators/pcsxr/")
			game_path = goodJoin('../../', data['path'] + '/' + data['binary'])
			command = '"pcsxr.exe" -nogui -cdfile "' + game_path + '"'
			runner = emu_runner.EmuRunner(command, 'PCSXR', full_screen_alt_enter=True)
			runner.run()
			os.chdir("../..")
			data = {
				'action' : 'log',
				'value' : 'playing'
			}
			self.write_data(data)
			print('Running PCSX-R ...')

		elif data['console'] == 'Playstation2':
			# Run the game
			os.chdir("emulators/pcsx2-v1.2.1-884-g2da3e15-windows-x86/")
			game_path = goodJoin("../../", data['path'] + '/' + data['binary'])
			command = '"pcsx2.exe" --nogui "' + game_path + '"'
			runner = emu_runner.EmuRunner(command, 'GSdx', full_screen_alt_enter=True)
			runner.run()
			os.chdir("../..")
			data = {
				'action' : 'log',
				'value' : 'playing'
			}
			self.write_data(data)
			print('Running PCSX2 ...')

	def _download_file(self, data):
		t = downloader.Downloader(data['url'], data['file'], data['dir'])
		t.daemon = True
		t.start()
		t.join()
		if not t.is_success:
			print(t.message)
			exit(1)

	def _is_installed(self, data):
		if data['program'] == 'VirtualCloneDrive':
			exist = os.path.exists("C:/Program Files (x86)/Elaborate Bytes/VirtualCloneDrive/VCDMount.exe")
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : 'VirtualCloneDrive'
			}
			self.write_data(data)
		elif data['program'] == 'NullDC':
			exist = os.path.exists("emulators/nullDC_104_r136/nullDC_Win32_Release-NoTrace.exe")
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : 'NullDC'
			}
			self.write_data(data)
		elif data['program'] == 'Demul':
			exist = os.path.exists("emulators/demul0582/demul.exe")
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
			exist = os.path.exists("emulators/pcsx2-v1.2.1-884-g2da3e15-windows-x86/pcsx2.exe")
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : 'PCSX2'
			}
			self.write_data(data)
		elif data['program'] == 'Mupen 64 Plus':
			exist = os.path.exists("emulators/mupen64plus-bundle-win32-2.0/mupen64plus.exe")
			data = {
				'action' : 'is_installed',
				'value' : exist,
				'name' : 'Mupen 64 Plus'
			}
			self.write_data(data)
		else:
			print('Unknown program to check if installed: {0}'.format(data['program']))


if __name__ == '__main__':
	icon = 'server/emu_archive.ico'
	script_path = os.path.dirname(os.path.realpath(__file__))
	icon = os.path.join(script_path, icon)
	hover_text = "Emu Archive"
	application = None
	server = None
	port = 9090
	server_thread = None

	def start(trayIcon):
		import threading

		# Generate the database of games
		make_db('gamecube.json', 'games/Nintendo/GameCube')
		make_db('nintendo64.json', 'games/Nintendo/Nintendo64')
		make_db('saturn.json', 'games/Sega/Saturn')
		make_db('dreamcast.json', 'games/Sega/Dreamcast')
		make_db('playstation.json', 'games/Sony/Playstation')
		make_db('playstation2.json', 'games/Sony/Playstation2')

		def start_server(port):
			global server
			global application

			application = tornado.web.Application([
				(r'/ws', WebSocketHandler),
				(r'/', MainHandler),
				(r'/index.html', MainHandler),
				(r'/configure.html', ConfigureHandler),
				(r"/(.*)", tornado.web.StaticFileHandler, {"path" : r"./"}),
			])

			application.listen(port)
			print('Server running on http://localhost:{0} ...'.format(port))
			server = tornado.ioloop.IOLoop.instance()
			server.start()

		# Start the server in its own thread
		server_thread = threading.Thread(target=start_server, args = (port, ))
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

	def demul(trayIcon):
		run_emulator("emulators/demul0582/", "demul.exe")

	def ssf(trayIcon):
		run_emulator("emulators/SSF_012_beta_R4/", "SSF.exe")

	def dolphin(trayIcon):
		run_emulator("emulators/Dolphin-x64/", "Dolphin.exe")

	def mupen64plus(trayIcon):
		run_emulator("emulators/mupen64plus-bundle-win32-2.0/", "mupen64plus.exe")

	def pcsxr(trayIcon):
		run_emulator("emulators/pcsxr/", "pcsxr.exe")

	def pcsx2(trayIcon):
		run_emulator("emulators/pcsx2-v1.2.1-884-g2da3e15-windows-x86/", "pcsx2.exe")

	def run_emulator(path, exe):
		if not os.path.exists(os.path.join(path, exe)):
			return

		os.chdir(path)
		proc = subprocess.Popen(exe, stdout=subprocess.PIPE)
		os.chdir("../..")

	menu_options = (
						('Start Server', icon, start),
						('Stop Server', icon, stop),
						('View in Browser', icon, view_in_browser),
						('Emulators', icon,
							(
								('Demul', icon, demul),
								('SSF', icon, ssf),
								('Dolphin', icon, dolphin),
								('Mupen 64 Plus', icon, mupen64plus),
								('PSX-Reloaded', icon, pcsxr),
								('PCSX2', icon, pcsx2),
							)
						)
					)

	tray_icon.TrayIcon(icon, hover_text, menu_options, on_quit=stop, on_start=start, default_menu_index=1)



