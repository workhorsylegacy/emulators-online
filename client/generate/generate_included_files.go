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

package main

import (
	"fmt"
	"log"
	//"io"
	"io/ioutil"
	"os"
	"os/exec"
	//"strings"
	"bytes"
	"compress/zlib"
	"encoding/base64"
	"encoding/gob"
)

func CompressWith7zip(in_file string, out_file string) {
	// Get the command and arguments
	command := "../../7za.exe"
	args := []string {
		"a",
		"-t7z",
		"-m0=lzma2",
		"-mx=9",
		fmt.Sprintf("%s", out_file),
		fmt.Sprintf("%s", in_file),
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

func main() {
	// Generate a file that will generate everything
	out, _ := os.Create("client/generated/generated_files.go")
	out.Write([]byte("package generated\r\n\r\n"))

	// Get a list of all the files to store
	file_names := []string {
		"unrarw32.exe",
		"about.html",
		"configure.html",
		"games.html",
		"index.html",
		"faq.html",
		"static/agplv3-155x51.png",
		"static/default.css",
		"static/emulators_online.js",
		"static/favicon.ico",
		"static/file_uploader.js",
		"static/input.js",
		"static/peer.js",
		"static/pako.min.js",
		"static/jquery-2.1.3.min.js",
		"static/web_socket.js",
		"client/identify_dreamcast_games/db_dreamcast_official_eu.json",
		"client/identify_dreamcast_games/db_dreamcast_official_jp.json",
		"client/identify_dreamcast_games/db_dreamcast_official_us.json",
		"client/identify_dreamcast_games/db_dreamcast_unofficial.json",
		"client/identify_dreamcast_games/identify_dreamcast_games.exe",
		"client/identify_playstation2_games/db_playstation2_official_as.json",
		"client/identify_playstation2_games/db_playstation2_official_au.json",
		"client/identify_playstation2_games/db_playstation2_official_eu.json",
		"client/identify_playstation2_games/db_playstation2_official_jp.json",
		"client/identify_playstation2_games/db_playstation2_official_ko.json",
		"client/identify_playstation2_games/db_playstation2_official_us.json",
		"client/identify_playstation2_games/identify_playstation2_games.exe",
		"licenses/license_7zip",
		"licenses/license_identify_dreamcast_games",
		"licenses/license_identify_playstation2_games",
		"licenses/license_iso9660",
		"licenses/license_py_read_udf",
		"licenses/license_read_udf",
		"licenses/license_unrar",
	}

	// Read the files into a map
	file_map := make(map[string][]byte)
	for _, file_name := range file_names {
		// Read the file to a string
		data, err := ioutil.ReadFile(file_name)
		if err != nil {
			log.Fatal(err)
		}

		// Put the file string into the map
		file_map[file_name] = data
	}

	// Convert the map to a gob
	var gob_buffer bytes.Buffer
	encoder := gob.NewEncoder(&gob_buffer)
	err := encoder.Encode(file_map)
	if err != nil {
		log.Fatal(err)
	}

	// Write the gob to file
	ioutil.WriteFile("client/generated/gob", gob_buffer.Bytes(), 0644)
	gob_buffer.Reset()

	// Compress the gob to file
	os.Chdir("client/generated")
	CompressWith7zip("gob", "gob.7z")
	os.Chdir("../..")

	// Read the compressed gob from file
	file_data, err := ioutil.ReadFile("client/generated/gob.7z")
	if err != nil {
		log.Fatal(err)
	}

	// Base64 the compressed gob
	base64ed_data := base64.StdEncoding.EncodeToString(file_data)

	// Write the files generating function
	out.Write([]byte("func GetCompressedFiles() string {\r\n"))
	out.Write([]byte("    return \""))
	out.Write([]byte(base64ed_data))
	out.Write([]byte("\"\r\n"))
	out.Write([]byte("}\r\n"))

	// Read 7zip into an array
	file_data, err = ioutil.ReadFile("7za.exe")
	if err != nil {
		log.Fatal(err)
	}

	// Convert the 7zip array to a gob
	encoder = gob.NewEncoder(&gob_buffer)
	err = encoder.Encode(file_data)
	if err != nil {
		log.Fatal(err)
	}

	// Compress the gob
	var zlib_buffer bytes.Buffer
	writer, err := zlib.NewWriterLevel(&zlib_buffer, zlib.BestCompression)
 	if err != nil {
 		log.Fatal(err)
 	}
	writer.Write(gob_buffer.Bytes())
	writer.Close()

	// Base64 the compressed gob
	base64ed_data = base64.StdEncoding.EncodeToString(zlib_buffer.Bytes())

	// Write the 7zip generating function
	out.Write([]byte("func GetCompressed7zip() string {\r\n"))
	out.Write([]byte("    return \""))
	out.Write([]byte(base64ed_data))
	out.Write([]byte("\"\r\n"))
	out.Write([]byte("}\r\n"))

	// Close the file
	out.Close()
}
