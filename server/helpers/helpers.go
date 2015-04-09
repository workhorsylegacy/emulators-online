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
	"os"
	"strings"
	"math"
)

func Round(f float64) float64 {
	return math.Floor(f + .5)
}

func RoundPlus(f float64, places int) (float64) {
	shift := math.Pow(10, float64(places))
	return Round(f * shift) / shift;
}

func SanitizeFileName(name string) string {
	sanitize_map := map[string]string {
		"/" : "+",
		"\\" : "+",
		": " : " - ",
		"*" : "+",
		"?" : "",
		"\"" : "'",
		"<" : "[",
		">" : "]",
		"|" : "+",
	}
	for before, after := range sanitize_map {
		name = strings.Replace(name, before, after, -1)
	}

	return name
}

func Between(original string, before string, after string) string {
	retval := strings.Split(original, before)[1]
	retval = strings.Split(retval, after)[0]
	return retval
}

func IsFile(file_name string) (bool) {
	// Get the file info
	finfo, err := os.Stat(file_name)

	// Return false if failed to get the file info
	if err != nil {
		return false
	}

	// Return false if it is a directory
	if finfo.IsDir() {
		return false
	}

	// Return true if it has a name
	if len(finfo.Name()) > 0 {
		return true
	}

	// Return false otherwise
	return false
}

func IsDir(dir_name string) (bool) {
	// Get the dir info
	finfo, err := os.Stat(dir_name)

	// Return false if failed to get the dir info
	if err != nil {
		return false
	}

	// Return true if it is a directory
	if finfo.IsDir() {
		return true
	}

	// Return false otherwise
	return false
}

func PathExists(path_name string) (bool) {
	// Get the dir info
	finfo, err := os.Stat(path_name)

	// Return false if failed to get the path info
	if err != nil {
		return false
	}

	// Return if it has a name
	if len(finfo.Name()) > 0 {
		return true
	}

	// Return false otherwise
	return true
}
