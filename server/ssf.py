
import os, sys

import ini
import file_mounter
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
	game_path = goodJoin("../../", path + '/' + binary)
	command = '"SSF.exe" "' + game_path + '"'
	runner = emu_runner.EmuRunner(command, 'SSF', full_screen_alt_enter=True)
	runner.run()
	os.chdir("../..")

