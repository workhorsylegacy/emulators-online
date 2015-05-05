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
	// Replace all the chars with the safe equiv
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

	// Remove any trailing periods
	name = strings.Trim(name, ".")

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
