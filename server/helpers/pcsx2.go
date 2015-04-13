// Copyright (c) 2015, Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
// emu_archive is a HTML based front end for video game console emulators
// It uses a MIT style license
// It is hosted at: https://github.com/workhorsy/emu_archive
//
// Permission is hereby granted, free of charge, to any person obtaining
// a copy of this software and associated documentation files (the
// "Software"), to deal in the Software without restriction, including
// without limitation the rights to use, copy, modify, merge, publish,
// distribute, sublicense, and/or sell copies of the Software, and to
// permit persons to whom the Software is furnished to do so, subject to
// the following conditions:
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
// EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
// MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
// IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
// CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
// TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
// SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


package helpers

import(
	"os"
	"strings"
	//"fmt"
	//"io/ioutil"
	"path/filepath"
	//"log"
)

type PCSX2 struct {
	*BaseConsole
}

func goodJoin(path_a string, path_b string) string {
	path := path_a + path_b
	path, _ = filepath.Abs(path)
	path = strings.Replace(path, "\\", "/", -1)
	return path
}

func (self *PCSX2) Run(path string, binary string) {
	// Figure out if running a game or not
	full_screen := false
	if binary != "" {
		full_screen = true
	} else {
		full_screen = false
	}

	os.Chdir("emulators/pcsx2-v1.3.1-93-g1aebca3-windows-x86/")
	game_path := goodJoin("../../", path + "/" + binary)
	command := CommandWithArgs {
		"pcsx2.exe",
		[]string {"--nogui", game_path},
	}

	// Run the game
	var runner EmuRunner
	full_screen_alt_enter := true
	runner.Setup(command, "GSdx", full_screen, full_screen_alt_enter)
	runner.Run()
	os.Chdir("../..")
}

