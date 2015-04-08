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
	"strings"
	"fmt"
	"io/ioutil"
	"log"
	"os/exec"
	"bytes"
)

var g_directx_version int
var g_version_channel chan int

func find_directx_version(version_channel chan int) {
	// Run dxdiag and write its output to a file
	cmd := exec.Command("dxdiag.exe", "/t", "directx_info.txt")
	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	if err != nil {
		fmt.Printf("Failed to determine DirectX version: %s\r\n", err)
		return
	}

	// Get the info from the file
	data, err := ioutil.ReadFile("directx_info.txt")
	if err != nil {
		fmt.Printf("Failed to determine DirectX version: %s\r\n", err)
		return
	}
	string_data := string(data)
	raw_version := Between(string_data, "DirectX Version: ", "\r\n")

	// Get the DirectX version
	var version int
	if strings.Contains(raw_version, "11") {
		version = 11
	} else if strings.Contains(raw_version, "10") {
		version = 10
	} else if strings.Contains(raw_version, "9") {
		version = 9
	} else {
		log.Fatal("Failed to determine DirectX version.\r\n")
	}

	version_channel <- version
}

func GetDirectXVersion() int {
	// Return the version if we already have it
	if g_directx_version > 0 {
		return g_directx_version
	}

	// Otherwise wait here for the version
	g_directx_version = <- g_version_channel
	return g_directx_version
}

func init() {
	// Start the goroutine that looks up the DirectX version
	g_version_channel = make(chan int)
	go find_directx_version(g_version_channel)
}


