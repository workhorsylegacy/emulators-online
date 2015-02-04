
import os, sys

import ini
import emu_runner

if sys.version_info[0] == 2:
	import ConfigParser as configparser
else:
	import configparser

def goodJoin(path_a, path_b):
	path = path_a + path_b
	path = os.path.abspath(path)
	path = path.replace("\\", "/")
	return path

def run(path, binary):
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
	game_path = goodJoin("../../", path + '/' + binary)
	command = '"Dolphin.exe" --batch --exec="' + game_path + '"'
	runner = emu_runner.EmuRunner(command, 'Dolphin 4.0', full_screen_alt_enter=True)
	runner.run()
	os.chdir("../..")
