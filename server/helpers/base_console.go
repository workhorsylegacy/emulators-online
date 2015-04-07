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
	//"fmt"
	"strings"
	"io/ioutil"
	"path/filepath"
	"os"
	//"runtime"
	//"log"
	//"os/exec"
	//"encoding/base64"
	"encoding/json"
)


type BaseConsole struct {
	config_path string
	button_map map[string]string
}

func (self *BaseConsole) Setup(config_path string) error {
	self.config_path = config_path
	//self.button_map = map[string]string{}

	// Load the config
	if IsFile(self.config_path) {
		data, err := ioutil.ReadFile(self.config_path)
		if err != nil {
			return err
		}
		err = json.Unmarshal(data, self.button_map)
		if err != nil {
			return err
		}
	}

	return nil
}

func (self *BaseConsole) SetButtonMap(button_map map[string]string) error {
	self.button_map = button_map

	// Open the file
	f, err := os.Open(self.config_path)
	if err != nil {
		return err
	}
	defer f.Close()

	// Convert the button map to json
	jsoned_data, err := json.MarshalIndent(self.button_map, "", "\t")
	if err != nil {
		return err
	}

	// Write the jsoned button map to file
	f.Write([]byte(jsoned_data))

	return nil
}

func (self *BaseConsole) GetButtonMap() map[string]string {
	return self.button_map
}

func (self *BaseConsole) goodJoin(path_a string, path_b string) string {
	path := path_a + path_b
	path, _ = filepath.Abs(path)
	path = strings.Replace(path, "\\", "/", -1)
	return path
}

