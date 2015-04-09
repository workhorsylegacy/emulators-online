package main

import (
	//"io"
	"io/ioutil"
	"os"
	//"strings"
	"encoding/base64"
)

// FIXME: Update to compress the files before base64ing them
func main() {
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
		"server/db_dreamcast_official_eu.json",
		"server/db_dreamcast_official_jp.json",
		"server/db_dreamcast_official_us.json",
		"server/db_dreamcast_unofficial.json",
		"server/db_playstation2_official_as.json",
		"server/db_playstation2_official_au.json",
		"server/db_playstation2_official_eu.json",
		"server/db_playstation2_official_jp.json",
		"server/db_playstation2_official_ko.json",
		"server/db_playstation2_official_us.json",
		"server/dolphin.py",
		"server/file_mounter.py",
		"server/identify_dreamcast_games.py",
		"server/identify_playstation2_games.py",
		"server/iso9660.py",
		"server/mupen64plus.py",
		"server/pcsx2.py",
		"server/pcsxr.py",
		"server/read_udf.py",
		"server/ssf.py",
		"server/tray_icon.py",
	}
	out, _ := os.Create("server/generated/generated_files.go")
	out.Write([]byte("package generated\r\n\r\n"))
	out.Write([]byte("func GeneratedFiles() map[string]string {\r\n"))
	out.Write([]byte("    return map[string]string {\r\n"))
	for _, file_name := range file_names {
		data, _ := ioutil.ReadFile(file_name)
		b64_data := base64.StdEncoding.EncodeToString(data)
		out.Write([]byte("        \"" + file_name + "\" : "))
		out.Write([]byte("\"" + b64_data + "\",\r\n"))
	}
	out.Write([]byte("    }\r\n"))
	out.Write([]byte("\r\n"))
	out.Write([]byte("}\r\n"))
	out.Close()
}
