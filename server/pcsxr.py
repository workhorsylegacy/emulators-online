
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
	os.chdir("emulators/pcsxr/")
	game_path = goodJoin('../../', path + '/' + binary)
	command = '"pcsxr.exe" -nogui -cdfile "' + game_path + '"'
	runner = emu_runner.EmuRunner(command, 'PCSXR', full_screen_alt_enter=True)
	runner.run()
	os.chdir("../..")

