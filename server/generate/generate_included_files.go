package main

import (
	//"io"
	"io/ioutil"
	"os"
	//"strings"
	"encoding/base64"
)

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
	}
	out, _ := os.Create("server/generated/generated_files.go")
	out.Write([]byte("package generated\r\n\r\n"))
	out.Write([]byte("import (\r\n"))
	out.Write([]byte("    \"os\"\r\n"))
	out.Write([]byte("    \"encoding/base64\"\r\n"))
	out.Write([]byte(")\r\n\r\n"))
	out.Write([]byte("var static_files map[string]string\r\n\r\n"))
	out.Write([]byte("func GenerateFiles() {\r\n"))
	out.Write([]byte("    static_files = map[string]string {\r\n"))
	for _, file_name := range file_names {
		data, _ := ioutil.ReadFile(file_name)
		b64_data := base64.StdEncoding.EncodeToString(data)
		out.Write([]byte("        \"" + file_name + "\" : "))
		out.Write([]byte("\"" + b64_data + "\",\r\n"))
	}
	out.Write([]byte("    }\r\n"))
	out.Write([]byte("    for file_name, b64_data := range static_files {\r\n"))
	out.Write([]byte("        f, _ := os.Open(file_name)\r\n"))
	out.Write([]byte("        data, _ := base64.StdEncoding.DecodeString(b64_data)\r\n"))
	out.Write([]byte("        f.Write(data)\r\n"))
	out.Write([]byte("        f.Close()\r\n"))
	out.Write([]byte("    }\r\n"))
	out.Write([]byte("\r\n"))
	out.Write([]byte("}\r\n"))
	out.Close()
}
