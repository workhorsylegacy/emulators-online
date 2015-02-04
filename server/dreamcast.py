

import os, sys

import ini
import emu_runner

def goodJoin(path_a, path_b):
	path = path_a + path_b
	path = os.path.abspath(path)
	path = path.replace("\\", "/")
	return path

def run(path, binary):
	# FIXME: We have to parse the ini file by hand because ConfigParser cannot read unicode
	config = ini.read_ini_file('emulators/Demul/Demul.ini')

	# Bios
	bios_path = os.path.abspath('emulators/Demul/roms/')
	config['files']['roms0'] = bios_path
	config['files']['romsPathsCount'] = '1'

	# Plugins
	plugins_path = os.path.abspath('emulators/Demul/plugins/')
	config['plugins']['directory'] = plugins_path

	# nvram
	nvram_path = os.path.abspath('emulators/Demul/nvram/')
	config['files']['nvram'] = nvram_path

	# Get the DirectX version
	directx_dll = config['plugins']['gpu']
	directx_version = None
	if directx_dll == 'gpuDX11.dll':
		directx_version = 'gpuDX11hw'
	elif directx_dll == 'gpuDX10.dll':
		directx_version = 'gpuDX10hw'

	# Save the ini file
	ini.write_ini_file('emulators/Demul/Demul.ini', config)

	# Run the game
	os.chdir("emulators/Demul/")
	game_path = goodJoin("../../", path + '/' + binary)
	command = '"demul.exe" -run=dc -image="' + game_path + '"'
	runner = emu_runner.EmuRunner(command, directx_version, full_screen_alt_enter=True)
	runner.run()
	os.chdir("../..")

