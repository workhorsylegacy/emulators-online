
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
	os.chdir("emulators/pcsx2-v1.3.1-8-gf88bea5-windows-x86/")
	game_path = goodJoin("../../", path + '/' + binary)
	command = '"pcsx2.exe" --nogui "' + game_path + '"'
	runner = emu_runner.EmuRunner(command, 'GSdx', full_screen_alt_enter=True)
	runner.run()
	os.chdir("../..")

