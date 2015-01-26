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
. Add searching by developer, publisher, year, and console
. Move the images to jpg and use their own repository
. How do we deal with games that use multiple disks in the UI?
. Update the dialog generation to be on click
. Give an option to upload a binary too.
. Have the server use a task bar applet for the UI
. Have Virtual Clone Drive not popup the mounted directory
. Have it auto download Virtual Clone Drive for emulators that need it
. Have it auto download and config emulators
. Support for games that use more than one disk
. Controller configs
. Memory configs
. Move the mouse cursor to the bottom left corner on start
"""

import os, sys
import win32gui
import win32con
import win32api
import platform
import json
import subprocess
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import time

PY2 = sys.version_info[0] == 2

if PY2:
	import ConfigParser as configparser
else:
	import configparser



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

class EmuRunner(object):
	def __init__(self, command, emu_title_bar_text, full_screen_alt_enter=False):
		self.emu_title_bar_text = emu_title_bar_text
		self.command = command
		self.full_screen_alt_enter = full_screen_alt_enter
		self.emu_proc = None
		self.foundWindows = []

	def run(self):
		def enumWindowFunc(hwnd, windowList):
			text = win32gui.GetWindowText(hwnd)
			className = win32gui.GetClassName(hwnd)
			if text.find(self.emu_title_bar_text) >= 0:
				windowList.append((hwnd, text, className))

		wait_time = 0.1

		# Start the program
		self.emu_proc = subprocess.Popen(self.command, stdout=subprocess.PIPE)

		# Wait for the program's window to actually be created
		time.sleep(wait_time)
		while True:
			print('Waiting ...')
			# Look through all the windows and find the one with the title bar text we want
			win32gui.EnumWindows(enumWindowFunc, self.foundWindows)

			# Sleep for a bit if the window was not found
			if not self.foundWindows:
				time.sleep(1)
			else:
				break

		# Focus the window
		time.sleep(wait_time)
		while True:
			print('Wating ...')
			# Look through all the windows and find the one with the title bar text we want
			win32gui.EnumWindows(enumWindowFunc, self.foundWindows)

			if not self.foundWindows:
				continue

			# Focus the window
			got_window = False
			for hwnd, text, className in self.foundWindows:
				try:
					# Show the window if it is minimized
					time.sleep(wait_time)
					win32gui.ShowWindow(hwnd, True)
					win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
					win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
					win32gui.SetActiveWindow(hwnd)
					#win32gui.SetForegroundWindow(hwnd)

					# Move the mouse to the window corner, click on it, and move the mouse to the corner
					time.sleep(wait_time)
					x, y, w, h = win32gui.GetWindowRect(hwnd)
					win32api.SetCursorPos((x+1, y+1))
					win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
					win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
					win32api.SetCursorPos((0, 0))
					got_window = True
					break
				except:
					raise
					
			if got_window:
				break;
				
		# Fullscreening the emu window with alt + enter if needed
		if self.full_screen_alt_enter:
			time.sleep(wait_time)
			win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
			win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
			time.sleep(2)
			win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
			win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)


	def stop(self):
		output = self.emu_proc.stdout.read()
		if not PY2:
			output = output.decode(encoding='UTF-8')
		return output

emu_runner = None

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		loader = tornado.template.Loader(".")
		self.write(loader.load("index.html").generate())

def goodJoin(path_a, path_b):
	path = path_a + path_b
	path = os.path.abspath(path)
	path = path.replace("\\", "/")
	return path

class WebSocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		print('Server starting ...')
		self.write_message("Server starting ...")

	def on_close(self):
		print('Server stopping ...')

	def on_message(self, message):
		global emu_runner

		data = json.loads(message)

		# Client wants to play a game
		if data['action'] == 'play':
			if data['console'] == 'GameCube':
				# Run the game
				os.chdir("emulators/Dolphin-x64/")
				game_path = goodJoin("../../", data['path'] + '/' + data['binary'])
				command = '"Dolphin.exe" --batch --exec="' + game_path + '"'
				emu_runner = EmuRunner(command, 'Dolphin', full_screen_alt_enter=True)
				emu_runner.run()
				os.chdir("../..")
				self.write_message("playing")
				print('Running Dolphin ...')

			elif data['console'] == 'Nintendo64':
				# Run the game
				os.chdir("emulators/mupen64plus-bundle-win32-2.0/")
				game_path = goodJoin("../../", data['path'] + '/' + data['binary'])
				command = '"Mupen64plus.exe" --fullscreen "' + game_path + '"'
				emu_runner = EmuRunner(command, 'Mupen64plus', full_screen_alt_enter=False)
				emu_runner.run()
				os.chdir("../..")
				self.write_message("playing")
				print('Running Mupen64plus ...')

			elif data['console'] == 'Saturn':
				# Mount the game
				mounter = FileMounter("D")
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
				emu_runner = EmuRunner(command, 'SSF', full_screen_alt_enter=True)
				emu_runner.run()
				os.chdir("../..")
				self.write_message("playing")
				print('Running SSF ...')

			elif data['console'] == 'Dreamcast':
				# Run the game
				os.chdir("emulators/demul0582/")
				game_path = goodJoin("../../", data['path'] + '/' + data['binary'])
				command = '"demul.exe" -run=dc -image="' + game_path + '"'
				emu_runner = EmuRunner(command, 'gpuDX11hw', full_screen_alt_enter=True)
				emu_runner.run()
				os.chdir("../..")
				self.write_message("playing")
				print('Running Demul ...')

			elif data['console'] == 'Playstation':
				# Run the game
				os.chdir("emulators/pcsxr/")
				game_path = goodJoin("../../", data['path'] + '/' + data['binary'])
				command = '"pcsxr.exe" -nogui -cdfile "' + game_path + '"'
				emu_runner = EmuRunner(command, 'PCSXR', full_screen_alt_enter=True)
				emu_runner.run()
				os.chdir("../..")
				self.write_message("playing")
				print('Running PCSX-R ...')

		# Unknown message from the client
		else:
			self.write_message("Unknown message from client: {0}".format(message))
			print('received:', message)

application = tornado.web.Application([
	(r'/ws', WebSocketHandler),
	(r'/', MainHandler),
	(r'/index.html', MainHandler),
	(r"/(.*)", tornado.web.StaticFileHandler, {"path" : r"./"}),
])

if __name__ == "__main__":
	make_db('gamecube.json', 'games/Nintendo/GameCube')
	make_db('nintendo64.json', 'games/Nintendo/Nintendo64')
	make_db('saturn.json', 'games/Sega/Saturn')
	make_db('dreamcast.json', 'games/Sega/Dreamcast')
	make_db('playstation.json', 'games/Sony/Playstation')

	port = 9090
	application.listen(port)
	print('Server running on http://localhost:{0} ...'.format(port))
	tornado.ioloop.IOLoop.instance().start()


