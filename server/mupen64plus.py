
import os, sys

import ini
import emu_runner

def goodJoin(path_a, path_b):
	path = path_a + path_b
	path = os.path.abspath(path)
	path = path.replace("\\", "/")
	return path

def run(path, binary):
	# Run the game
	os.chdir("emulators/Mupen64Plus/")
	game_path = goodJoin("../../", path + '/' + binary)
	command = '"Mupen64plus.exe" --fullscreen "' + game_path + '"'
	runner = emu_runner.EmuRunner(command, 'Mupen64Plus', full_screen_alt_enter=False)
	runner.run()
	os.chdir("../..")

