// Copyright (c) 2015, Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
// emulators-online is a HTML based front end for video game console emulators
// It uses a MIT style license
// It is hosted at: https://github.com/workhorsy/emulators-online
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
	"io/ioutil"
	"strings"
	"os"
	"fmt"
	"log"
)


func ReadIniFile(file_path string) (map[string]map[string]interface{}, error) {
	data, err := ioutil.ReadFile(file_path)
	if err != nil {
		return nil, err
	}
	ini_data := string(data)
	var config map[string]map[string]interface{}

	// Read the ini file into a dictionary
	var header string
	for _, line := range strings.Split(ini_data, "\r\n") {
		// Line is a header
		if strings.Contains(line, "[") && strings.Contains(line, "]") {
			header = Between(line, "[", "]")
		// Line is a key value pair
		} else if strings.Contains(line, " = ") {
			pair := strings.Split(line, " = ")
			key, value := pair[0], pair[1]
			config[header][key] = value
		}
	}

	return config, err
}


func WriteIniFile(file_name string, config map[string]map[string]interface{}) error {
	f, err := os.Create(file_name)
	if err != nil {
		log.Fatal(err)
		return err
	}
	defer f.Close()

	// First add any fields with no master
	if pairs, ok := config[""]; ok {
		// Keys and values
		for key, value := range pairs {
			formatted_entry := fmt.Sprintf("%s = %v\r\n", key, value)
			f.Write([]byte(formatted_entry))
		}
	}

	// Add fields with a master
	for header, pairs := range config {
		// Skip if there is no master
		if header == "" {
			continue
		}

		// Header
		formatted_header := fmt.Sprintf("[%s]\r\n", header)
		f.Write([]byte(formatted_header))

		// Keys and values
		for key, value := range pairs {
			formatted_entry := fmt.Sprintf("%s = %v\r\n", key, value)
			f.Write([]byte(formatted_entry))
		}

		// Two spaces at the end of a section
		f.Write([]byte("\r\n\r\n"))
	}

	return nil
}





