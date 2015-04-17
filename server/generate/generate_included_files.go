package main

import (
	"log"
	//"io"
	"io/ioutil"
	"os"
	//"strings"
	"bytes"
	"compress/zlib"
	"encoding/base64"
	"encoding/gob"
	"fmt"
)


func main() {
	// Get a list of all the files to store
	file_names := []string {
		"configure.html",
		"index.html",
		"static/default.css",
		"static/emu_archive.js",
		"static/favicon.ico",
		"static/file_uploader.js",
		"static/input.js",
		"static/jquery-2.1.3.min.js",
		"static/web_socket.js",
		"server/identify_dreamcast_games/db_dreamcast_official_eu.json",
		"server/identify_dreamcast_games/db_dreamcast_official_jp.json",
		"server/identify_dreamcast_games/db_dreamcast_official_us.json",
		"server/identify_dreamcast_games/db_dreamcast_unofficial.json",
		"server/identify_dreamcast_games/identify_dreamcast_games.exe",
		"server/identify_playstation2_games/db_playstation2_official_as.json",
		"server/identify_playstation2_games/db_playstation2_official_au.json",
		"server/identify_playstation2_games/db_playstation2_official_eu.json",
		"server/identify_playstation2_games/db_playstation2_official_jp.json",
		"server/identify_playstation2_games/db_playstation2_official_ko.json",
		"server/identify_playstation2_games/identify_playstation2_games.exe",
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

	// Convert the map to binary
	var gob_buffer bytes.Buffer
	encoder := gob.NewEncoder(&gob_buffer)
	err := encoder.Encode(file_map)
	if err != nil {
		log.Fatal(err)
	}

	// Compress the binary map
	var zlib_buffer bytes.Buffer
	writer, err := zlib.NewWriterLevel(&zlib_buffer, zlib.BestCompression)
	if err != nil {
		log.Fatal(err)
	}
	writer.Write(gob_buffer.Bytes())
	writer.Close()

	// Base64 the compressed binary map
	base64ed_data := base64.StdEncoding.EncodeToString(zlib_buffer.Bytes())

	// Generate a file that will store everything
	out, _ := os.Create("server/generated/generated_files.go")
	out.Write([]byte("package generated\r\n\r\n"))
	out.Write([]byte("func GeneratedFiles() string {\r\n"))
	out.Write([]byte("    return \""))
	out.Write([]byte(base64ed_data))
	out.Write([]byte("\"\r\n"))
	out.Write([]byte("}\r\n"))
	out.Close()
}
