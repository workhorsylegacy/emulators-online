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

import (
	"fmt"
	"os/exec"
	"bytes"
	"log"
)

type Wrap7zip struct {
	exe string
}

func Setup(self *Wrap7zip) {
	// Check if 7zip is installed
	if IsFile("C:/Program Files/7-Zip/7z.exe") {
		self.exe = "C:/Program Files/7-Zip/7z.exe"
	} else if IsFile("C:/Program Files (x86)/7-Zip/7z.exe") {
		self.exe = "C:/Program Files (x86)/7-Zip/7z.exe"
	} else {
		log.Fatal("7-Zip wrapper could not locate 7z.exe\r\n")
	}
}

func Uncompress(self *Wrap7zip, compressed_file string, out_dir string) {
	fmt.Printf("!!!!!!!!!!!!!! uncomressing!\r\n")

	// Get the command and arguments
	command := fmt.Sprintf(`%s`, self.exe)
	args := []string {
		"x",
		"-y",
		fmt.Sprintf(`%s`, compressed_file),
		fmt.Sprintf("-o%s", out_dir),
	}

	// Run the command and wait for it to complete
	cmd := exec.Command(command, args...)
	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	if err != nil {
		fmt.Printf("Failed to run command: %s\r\n", err)
	}
}






