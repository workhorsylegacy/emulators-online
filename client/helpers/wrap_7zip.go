// Copyright (c) 2015, Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
// emulators-online is a HTML based front end for video game console emulators
// It uses the GNU AGPL 3 license
// It is hosted at: https://github.com/workhorsy/emulators-online
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

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






