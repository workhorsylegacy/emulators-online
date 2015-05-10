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
	"io"
	"fmt"
	"strings"
	//"time"
	//"runtime"
	"runtime/debug"
	"io/ioutil"
	"path/filepath"
	"os"
	"errors"
	"log"
	"os/exec"
	"compress/zlib"
	"encoding/base64"
	"encoding/json"
	"encoding/gob"
	"bytes"
	"strconv"
	//"net/url"

	"net/http"
	"golang.org/x/net/websocket"

	"emulators-online/client/helpers"
	"emulators-online/client/win32"
	"emulators-online/client/generated"
)

var g_ws *websocket.Conn

var g_websocket_needs_restart bool

type LongRunningTask struct {
	name string
	percentage float64
}

//type Dolphin struct {}
//type SSF struct {}
//type Mupen64Plus struct {}
//type PCSXR struct {}

// db is accessed like db[console][game][binary_name]
var db map[string]map[string]map[string]interface{}
var file_modify_dates map[string]map[string]int64
var long_running_tasks map[string]LongRunningTask
var demul *helpers.Demul
//var dolphin Dolphin
//var ssf SSF
//var mupen64plus Mupen64Plus
//var pcsxr PCSXR
var pcsx2 *helpers.PCSX2

var consoles []string

func CleanPath(file_path string) string {
	// Fix the backward slashes from Windows
	new_path := strings.Replace(file_path, "\\", "/", -1)

	// Strip off the Disc number
	if strings.Contains(new_path, " [Disc") {
		new_path = strings.Split(new_path, " [Disc")[0]
	}

	// Make sure it ends with a slash
	if ! strings.HasSuffix(new_path, "/") {
		new_path += "/"
	}

	return new_path
}

func AbsPath(file_path string) string {
	file_path, _ = filepath.Abs(file_path)
	file_path = strings.Replace(file_path, "\\", "/", -1)
	return file_path
}

func WebSocketSend(thing interface{}) error {
	//fmt.Printf("WebSocketSend ????????????????????????????????????????\r\n")

	// Convert the object to base64ed json
	message, err := ToBase64Json(thing)
	if err != nil {
		fmt.Printf("Failed to encode websocket message: %s\r\n", err)
		return err
	}
	//fmt.Printf("message: %s\r\n", message)

	// Get the header
	whole_message := fmt.Sprintf("%d:%s", len(message), message)
	//fmt.Printf("whole_message: %s\r\n", whole_message)

	// Write the message
	buffer := []byte(whole_message)
	write_len, err := g_ws.Write(buffer)
	if err != nil {
		g_websocket_needs_restart = true
		fmt.Printf("Failed to write websocket message: %s\r\n", err)
		return err
	}
	if write_len != len(buffer) {
		return errors.New("Whole buffer was not written to websocket\r\n")
	}
	//fmt.Printf("write_len: %d\r\n", write_len)

	return nil
}

func WebSocketRecieve() (map[string]interface{}, error) {
	//fmt.Printf("WebSocketRecieve ???????????????????????????????????\r\n")
	buffer := make([]byte, 20)

	// Read the message header
	read_len, err := g_ws.Read(buffer)
	if err != nil {
		fmt.Printf("Failed to read websocket message: %s\r\n", err)
		return nil, err
	}
	//fmt.Printf("read_len: %d\r\n", read_len)

	// Get the message length
	message := string(buffer[0 : read_len])
	chunks := strings.Split(message, ":")
	message_length64, _ := strconv.ParseInt(chunks[0], 10, 0)
	message_length := int(message_length64)
	message = chunks[1]
	message_length -= len(message)

	// Read the rest of the message
	for {
		buffer = make([]byte, message_length)
		read_len, err = g_ws.Read(buffer)
		if err != nil {
			fmt.Printf("Failed to read websocket message: %s\r\n", err)
			return nil, err
		}
		message += string(buffer[0 : read_len])
		message_length -= read_len
		if message_length < 1 {
			break
		}
	}

	// Convert the message from base64 and json
	thing, err := FromBase64Json(message)
	if err != nil {
		fmt.Printf("Failed to decode websocket message: %s\r\n", err)
		//fmt.Printf("message: %s\r\n", message)
		//decoded_message, err := base64.StdEncoding.DecodeString(message)
		//fmt.Printf("decoded_message: %s\r\n", decoded_message)
		return nil, err
	}

	//fmt.Printf("thing: %s\r\n", thing)
	return thing, nil
}

func FromBase64Json(message string) (map[string]interface{}, error) {
	var retval map[string]interface{}

	// Unbase64 the message
	buffer, err := base64.StdEncoding.DecodeString(message)
	if err != nil {
		return nil, err
	}
	
	// Unjson the message
	err = json.Unmarshal(buffer, &retval)
	if err != nil {
		return nil, err
	}

	return retval, nil
}

func ToBase64Json(thing interface{}) (string, error) {
	// Convert the object to json
	jsoned_data, err := json.MarshalIndent(thing, "", "\t")
	if err != nil {
		return "", err
	}

	// Convert the jsoned object to base64
	b64ed_data := base64.StdEncoding.EncodeToString(jsoned_data)
	if err != nil {
		return "", err
	}
	b64ed_and_jsoned_data := string(b64ed_data)

	return b64ed_and_jsoned_data, err
}

func FromCompressedBase64Json(message string) (map[string]map[string]map[string]interface{}, error) {
	var retval map[string]map[string]map[string]interface{}

	// Unbase64 the message
	unbase64ed_message, err := base64.StdEncoding.DecodeString(message)
	if err != nil {
		return nil, err
	}

	// Uncompress the message
	zlibed_buffer := bytes.NewBuffer([]byte(unbase64ed_message))
	var uncompressed_buffer bytes.Buffer
	reader, err := zlib.NewReader(zlibed_buffer)
	if err != nil {
		log.Fatal(err)
	}
	io.Copy(&uncompressed_buffer, reader)

	// Unjson the message
	err = json.Unmarshal(uncompressed_buffer.Bytes(), &retval)
	if err != nil {
		return nil, err
	}

	return retval, nil
}

func ToCompressedBase64Json(thing interface{}) (string, error) {
	// Convert the object to json
	jsoned_data, err := json.MarshalIndent(thing, "", "\t")
	if err != nil {
		return "", err
	}

	// Compress the jsoned object
	var out_buffer bytes.Buffer
	writer := zlib.NewWriter(&out_buffer)
	writer.Write([]byte(jsoned_data))
	writer.Close()

	// Convert the compressed object to base64
	b64ed_data := base64.StdEncoding.EncodeToString(out_buffer.Bytes())
	if err != nil {
		return "", err
	}
	b64ed_and_jsoned_data := string(b64ed_data)

	return b64ed_and_jsoned_data, err
}

func getDB() {
	message := map[string]interface{} {
		"action" : "get_db",
		"value" : db,
	}
	WebSocketSend(message)
}

func setDB(console_data map[string]map[string]map[string]interface{}) {
	// Just return if we are running any long running tasks
	if len(long_running_tasks) > 0 {
		return
	}

	// Loading existing game database
	if console_data != nil {
		// Load the game database
		db = console_data

		for _, console := range consoles {
			// Get the names of all the games
			keys := []string{}
			for k := range db[console] {
				keys = append(keys, k)
			}

			// Remove any games if there is no game file
			for _, name := range keys {
				data := db[console][name]
				binary := data["binary"].(string)
				if ! helpers.IsFile(binary) {
					delete(db[console], name)
				}
			}
		}
	// Loading blank game database
	} else {
		// Re Initialize the globals
		db = make(map[string]map[string]map[string]interface{})
		file_modify_dates = map[string]map[string]int64{}

		for _, console := range consoles {
			db[console] = make(map[string]map[string]interface{})
			file_modify_dates[console] = map[string]int64{}
		}
	}
}

func getDirectXVersion() {
	message := map[string]interface{} {
		"action" : "get_directx_version",
		"value" : helpers.GetDirectXVersion(),
	}
	WebSocketSend(message)
}

func setBios(data map[string]interface{}) (error) {
	console := data["console"].(string)
	type_name := data["type"].(string)
	value := data["value"].(string)
	is_default := data["is_default"].(bool)
	data_type := data["type"].(string)

	if console == "playstation2" {
		// Make the BIOS dir if missing
		if ! helpers.IsDir("emulators/pcsx2/bios") {
			os.Mkdir("emulators/pcsx2/bios", os.ModeDir)
		}

		// Convert the base64 data to BIOS and write to file
		file_name := filepath.Join("emulators/pcsx2/bios/", data_type)
		f, err := os.Create(file_name)
		if err != nil {
			fmt.Printf("Failed to save BIOS file: %s\r\n", err)
			return err
		}
		b642_data, err := base64.StdEncoding.DecodeString(value)
		if err != nil {
			fmt.Printf("Failed to un base64 BIOS file: %s\r\n", err)
			return err
		}
		f.Write(b642_data)
		f.Close()

		// If the default BIOS, write the name to file
		if is_default {
			err := ioutil.WriteFile("emulators/pcsx2/bios/default_bios", []byte(data_type), 0644)
			if err != nil {
				log.Fatal(err)
			}
		}
	} else if console == "dreamcast" {
		// Make the BIOS dir if missing
		if ! helpers.IsDir("emulators/Demul/roms") {
			os.Mkdir("emulators/Demul/roms", os.ModeDir)
		}

		// Get the BIOS file name
		var file_name string
		switch type_name {
			case "awbios.zip":
				file_name = "emulators/Demul/roms/awbios.zip"
			case "dc.zip":
				file_name = "emulators/Demul/roms/dc.zip"
			case "naomi.zip":
				file_name = "emulators/Demul/roms/naomi.zip"
			case "naomi2.zip":
				file_name = "emulators/Demul/roms/naomi2.zip"
		}

		// Convert the base64 data to BIOS and write to file
		f, err := os.Create(file_name)
		if err != nil {
			fmt.Printf("Failed to save BIOS file: %s\r\n", err)
			return err
		}
		b642_data, err := base64.StdEncoding.DecodeString(value)
		if err != nil {
			fmt.Printf("Failed to un base64 BIOS file: %s\r\n", err)
			return err
		}
		f.Write(b642_data)
		f.Close()
	} else if console == "saturn" {
		// Make the BIOS dir if missing
		if ! helpers.IsDir("emulators/SSF_012_beta_R4/bios") {
			os.Mkdir("emulators/SSF_012_beta_R4/bios", os.ModeDir)
		}

		// Get the BIOS file name
		var file_name string
		switch type_name {
			case "USA":
				file_name = "emulators/SSF_012_beta_R4/bios/Sega Saturn BIOS (US).bin"
			case "EUR":
				file_name = "emulators/SSF_012_beta_R4/bios/Sega Saturn BIOS (EUR).bin"
			case "JAP":
				file_name = "emulators/SSF_012_beta_R4/bios/Sega Saturn BIOS (JAP).bin"
		}

		// Convert the base64 data to BIOS and write to file
		f, err := os.Create(file_name)
		if err != nil {
			return err
		}
		b642_data, _ := base64.StdEncoding.DecodeString(value)
		f.Write(b642_data)
		f.Close()
	}

	return nil
}

func setButtonMap(data map[string]interface{})  {
	// Convert the map[string]interface to map[string]string
	button_map := make(map[string]string)
	value := data["value"].(map[string]interface{})
	for key, value := range value {
		button_map[key] = value.(string)
	}

	switch data["console"].(string) {
		case "gamecube":
			//dolphin.SetButtonMap(button_map)

		case "nintendo64":
			//mupen64plus.SetButtonMap(button_map)

		case "saturn":
			//ssf.SetButtonMap(button_map)

		case "dreamcast":
			demul.SetButtonMap(button_map)

		case "Playstation":
			//pcsxr.SetButtonMap(button_map)

		case "playstation2":
			pcsx2.SetButtonMap(button_map)
	}
}

func getButtonMap(data map[string]interface{}) {
	var value map[string]string
	console := data["console"].(string)

	switch console {
		case "gamecube":
			//value = dolphin.GetButtonMap()

		case "nintendo64":
			//value = mupen64plus.GetButtonMap()

		case "saturn":
			//value = ssf.GetButtonMap()

		case "dreamcast":
			value = demul.GetButtonMap()

		case "Playstation":
			//value = pcsxr.GetButtonMap()

		case "playstation2":
			value = pcsx2.GetButtonMap()
	}

	message := map[string]interface{} {
		"action" : "get_button_map",
		"value" : value,
		"console" : console,
	}
	WebSocketSend(&message)
}


func taskGetGameInfo(channel_task_progress chan LongRunningTask, channel_is_done chan bool, data map[string]interface{}) error {
	directory_name := data["directory_name"].(string)
	console := data["console"].(string)

	// Add the thread to the list of long running tasks
	a_task := LongRunningTask {
		fmt.Sprintf("Searching for %s games", console),
		0,
	}
	channel_task_progress <- a_task

	// Get the path for this console
	var path_prefix string
	switch console {
		case "gamecube":
			path_prefix = "images/Nintendo/GameCube"
		case "nintendo64":
			path_prefix = "images/Nintendo/Nintendo64"
		case "saturn":
			path_prefix = "images/Sega/Saturn"
		case "dreamcast":
			path_prefix = "images/Sega/Dreamcast"
		case "playstation1":
			path_prefix = "images/Sony/Playstation1"
		case "playstation2":
			path_prefix = "images/Sony/Playstation2"
	}

	// Get the total number of files
	total_files := 0.0
	filepath.Walk(directory_name, func(path string, _ os.FileInfo, _ error) error {
		total_files += 1.0
		return nil
	})

	// Walk through all the directories
	done_files := 0.0
	filepath.Walk(directory_name, func(file string, _ os.FileInfo, _ error) error {
		// Get the full path
		entry := file
		entry, _ = filepath.Abs(entry)
		entry = strings.Replace(entry, "\\", "/", -1)

		// Get the percentage of the progress looping through files
		percentage := (done_files / total_files) * 100.0
		a_task.percentage = percentage
		channel_task_progress <- a_task
		done_files += 1.0

		// Skip if the the entry is not a file
		if ! helpers.IsFile(entry) {
			return nil
		}

		// Skip if the game file has not been modified
		var old_modify_date int64 = 0
		if val, ok := file_modify_dates[console][entry]; ok {
			old_modify_date = val
		}
		finfo, err := os.Stat(entry)
		if err != nil {
			return nil
		}
		modify_date := finfo.ModTime().UnixNano()
		if modify_date == old_modify_date {
			return nil
		} else {
			file_modify_dates[console][entry] = modify_date
		}

		// Get the game info
		var info map[string]interface{}
		var cmd *exec.Cmd
		if console == "dreamcast" {
			cmd = exec.Command("client/identify_dreamcast_games/identify_dreamcast_games.exe", entry)
		} else if console == "playstation2" {
			cmd = exec.Command("client/identify_playstation2_games/identify_playstation2_games.exe", entry)
		} else {
			log.Fatal(fmt.Sprintf("Unexpected console: %s", console))
		}

		// Run the command and get the info for this game
		var out bytes.Buffer
		cmd.Stdout = &out
		err = cmd.Run()
		if err != nil {
			fmt.Printf("Failed to get game info for file: %s\r\n", entry)
			return nil
		}
		out_bytes := out.Bytes()
		if len(out_bytes) > 0 {
			err := json.Unmarshal(out_bytes, &info)
			if err != nil {
				fmt.Printf("Failed to convert json to map: %s\r\n%s\r\n", err, string(out_bytes))
				return nil
			}
		} else {
			return nil
		}
		if err != nil {
			fmt.Printf("Failed to find info for game \"%s\"\r\n%s\r\n", entry, err)
			return nil
		}
		fmt.Printf("getting game info: %s\r\n", info["title"].(string))
		info["file"] = entry

		// Save the info in the db
		if info != nil {
			title := info["title"].(string)
			clean_title := helpers.SanitizeFileName(title)

			// Initialize the db for this console if needed
			if _, ok := db[console]; !ok {
				db[console] = make(map[string]map[string]interface{})
			}

			db[console][title] = map[string]interface{} {
				"path" : CleanPath(fmt.Sprintf("%s/%s/", path_prefix, clean_title)),
				"binary" : AbsPath(info["file"].(string)),
				"bios" : "",
				"images" : []string{},
				"developer" : "",
				"publisher" : "",
				"genre" : "",
			}

			if val, ok := info["developer"]; ok {
				db[console][title]["developer"] = val
			}

			if val, ok := info["publisher"]; ok {
				db[console][title]["publisher"] = val
			}

			if val, ok := info["genre"]; ok {
				db[console][title]["genre"] = val
			}

			// Get the images
			image_dir := fmt.Sprintf("%s/%s/", path_prefix, title)
			expected_images := []string{"title_big.png", "title_small.png"}
			for _, img := range expected_images {
				if ! helpers.IsDir(image_dir) {
					image_file := fmt.Sprintf("%s%s", image_dir, img)
					if helpers.IsFile(image_file) {
						images := db[console][title]["images"].([]string)
						images = append(images, image_file)
						db[console][title]["images"] = images
					}
				}
			}
		}
		return nil
	})

	// Send the updated game db to the browser
	value, err := ToCompressedBase64Json(db)
	if err != nil {
		log.Fatal(err)
	}
	
	message := map[string]interface{} {
		"action" : "set_db",
		"value" : value,
	}
	WebSocketSend(&message)
/*
	// Write the db cache file
	f, err := os.Create(fmt.Sprintf("cache/game_db_%s.json", console))
	defer f.Close()
	if err != nil {
		fmt.Printf("Failed to open cache file: %s\r\n", err)
		return err
	}
	jsoned_data, err := json.MarshalIndent(db[console], "", "\t")
	if err != nil {
		fmt.Printf("Failed to convert db to json: %s\r\n", err)
		return err
	}
	f.Write(jsoned_data)
*/

	// Write the modify dates cache file
	f, err := os.Create(fmt.Sprintf("cache/file_modify_dates_%s.json", console))
	defer f.Close()
	if err != nil {
		fmt.Printf("Failed to open file modify dates file: %s\r\n", err)
		return err
	}
	jsoned_data, err := json.MarshalIndent(file_modify_dates[console], "", "\t")
	if err != nil {
		fmt.Printf("Failed to convert file_modify_dates to json: %s\r\n", err)
		return err
	}
	f.Write(jsoned_data)

	fmt.Printf("Done getting games from directory.\r\n")

	a_task.percentage = 100.0
	channel_task_progress <- a_task

	// Signal that we are done
	channel_is_done <- true
	return nil
}

func setGameDirectory(data map[string]interface{}) {
	// Just return if there is already a long running "Searching for dreamcast games" task
	name := fmt.Sprintf("Searching for %s games", data["console"].(string))
	if _, ok := long_running_tasks[name]; ok {
		return
	}

	// Run a goroutine that will look through all the games and get their info
	channel_task_progress := make(chan LongRunningTask)
	channel_is_done := make(chan bool)
	go taskGetGameInfo(channel_task_progress, channel_is_done, data)

	// Wait for the goroutine to send its info and exit
	for {
		select {
			case is_done := <-channel_is_done:
				if is_done {
					return
				}
			case long_running_task := <-channel_task_progress:
				// Update its percentage
				long_running_tasks[long_running_task.name] = long_running_task

				// Remove the task if it is at 100 percent
				if long_running_task.percentage >= 100.0 {
					delete(long_running_tasks, long_running_task.name)
				}

				// Convert the list of long running tasks to a map
				shit := map[string]float64{}
				for name, task := range long_running_tasks {
					percentage := task.percentage
					shit[name] = percentage
				}

				// Send the websocket the new map of long running tasks
				message := map[string]interface{} {
					"action" : "long_running_tasks",
					"value" : shit,
				}
				WebSocketSend(&message)
		}
	}
}

func saveMemoryCardCB(memory_card []byte) {
	var out_buffer bytes.Buffer
	writer := zlib.NewWriter(&out_buffer)
	writer.Write([]byte(memory_card))
	writer.Close()
	// FIXME: Send the memory card to the server
	fmt.Printf("FIXME: Memory card needs saving. length %v\r\n", out_buffer.Len())
}

func playGame(data map[string]interface{}) {
	console := data["console"].(string)
	path := data["path"].(string)
	binary := data["binary"].(string)
	//bios := data["bios"].(string)

	switch console {
		case "gamecube":
			//dolphin.Run(path, binary)
			//self.log("playing")
			fmt.Printf("Running Dolphin ...\r\n")

		case "nintendo64":
			//mupen64plus.Run(path, binary)
			//self.log("playing")
			fmt.Printf("Running Mupen64plus ...\r\n")

		case "saturn":
			//ssf.Run(path, binary, bios)
			//self.log("playing")
			fmt.Printf("Running SSF ...\r\n")

		case "dreamcast":
			demul.Run(path, binary, saveMemoryCardCB)
			//self.log("playing")
			fmt.Printf("Running Demul ...\r\n")

		case "Playstation":
			//pcsxr.Run(path, binary)
			//self.log("playing")
			fmt.Printf("Running PCSX-Reloaded ...\r\n")

		case "playstation2":
			pcsx2.Run(path, binary)
			//self.log("playing")
			fmt.Printf("Running PCSX2 ...\r\n")
	}
}

func progressCB(name string, progress float64) {
	message := map[string]interface{} {
		"action" : "progress",
		"value" : progress,
		"name" : name,
	}
	WebSocketSend(&message)
}

func downloadFile(data map[string]interface{}) {
	// Get all the info we need
	file_name := data["file"].(string)
	url := data["url"].(string)
	directory := data["dir"].(string)
	name := data["name"].(string)
	referer := data["referer"].(string)

	// Download the file header
	client := &http.Client{}
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Set("Referer", referer)
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36")
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("Download failed: %s\r\n", err)
		return
	}
	if resp.StatusCode != 200 {
		fmt.Printf("Download failed with response code: %s\r\n", resp.Status)
		return
	}
	content_length := float64(resp.ContentLength)
	total_length := 0.0

	// Create the out file
	buffer := make([]byte, 32 * 1024)
	out, err := os.Create(filepath.Join(directory, file_name))
	if err != nil {
		fmt.Printf("Failed to create output file: %s\r\n", err)
		return
	}

	// Close the files when we exit
	defer out.Close()
	defer resp.Body.Close()

	// Download the file one chunk at a time
	EOF := false
	for {
		// Read the next chunk
		read_len, err := resp.Body.Read(buffer)
		if err != nil {
			if err.Error() == "EOF" {
				EOF = true
			} else {
				fmt.Printf("Download next chunk failed: %s\r\n", err)
				return
			}
		}

		// Write the next chunk to file
		write_len, err := out.Write(buffer[0 : read_len])
		if err != nil {
			fmt.Printf("Writing chunk to file failed: %s\r\n", err)
			return
		}

		// Make sure everything read was written
		if read_len != write_len {
			fmt.Printf("Write and read length were different\r\n")
			return
		}

		// Fire the progress callback
		total_length += float64(read_len)
		progress := helpers.RoundPlus((total_length / content_length) * 100.0, 2)
		progressCB(name, progress)

		// Exit the loop if the file is done
		if EOF || total_length == content_length {
			break
		}
	}
}

func install(data map[string]interface{}) {
	dir := data["dir"].(string)
	file := data["file"].(string)

	// Start uncompressing
	message := map[string]interface{}{
		"action" : "uncompress",
		"is_start" : true,
		"name" : file,
	}
	WebSocketSend(&message)

	switch file {
	case "SetupVirtualCloneDrive.exe":
		os.Chdir(dir)
		cmd := exec.Command(file, "/S")
		var out bytes.Buffer
		cmd.Stdout = &out
		cmd.Run()
		os.Chdir("..")
	case "7z920.exe":
		os.Chdir(dir)
		cmd := exec.Command(file, "/S")
		var out bytes.Buffer
		cmd.Stdout = &out
		cmd.Run()
		os.Chdir("..")
	case "nullDC_104_r136.7z":
		wrap := helpers.Wrap7zip{}
		helpers.Setup(&wrap)
		helpers.Uncompress(&wrap, filepath.Join(dir, "nullDC_104_r136.7z"), "emulators/NullDC")
	case "demul0582.rar":
		wrap := helpers.Wrap7zip{}
		helpers.Setup(&wrap)
		helpers.Uncompress(&wrap, filepath.Join(dir, "demul0582.rar"), "emulators/Demul")
	case "SSF_012_beta_R4.zip":
		wrap := helpers.Wrap7zip{}
		helpers.Setup(&wrap)
		helpers.Uncompress(&wrap, filepath.Join(dir, "SSF_012_beta_R4.zip"), "emulators")
	case "dolphin-master-4.0-5363-x64.7z":
		wrap := helpers.Wrap7zip{}
		helpers.Setup(&wrap)
		helpers.Uncompress(&wrap, filepath.Join(dir, "dolphin-master-4.0-5363-x64.7z"), "emulators")
	case "mupen64plus-bundle-win32-2.0.zip":
		wrap := helpers.Wrap7zip{}
		helpers.Setup(&wrap)
		helpers.Uncompress(&wrap, filepath.Join(dir, "mupen64plus-bundle-win32-2.0.zip"), "emulators/Mupen64Plus")
	case "pcsxr-1.9.93-win32.zip":
		wrap := helpers.Wrap7zip{}
		helpers.Setup(&wrap)
		helpers.Uncompress(&wrap, filepath.Join(dir, "pcsxr-1.9.93-win32.zip"), "emulators")
	case "pcsx2-v1.3.1-93-g1aebca3-windows-x86.7z":
		wrap := helpers.Wrap7zip{}
		helpers.Setup(&wrap)
		helpers.Uncompress(&wrap, filepath.Join(dir, "pcsx2-v1.3.1-93-g1aebca3-windows-x86.7z"), "emulators")
		err := os.Rename("emulators/pcsx2-v1.3.1-93-g1aebca3-windows-x86", "emulators/pcsx2")
		if err != nil {
			log.Fatal(err)
		}
	}

	// End uncompressing
	message = map[string]interface{}{
		"action" : "uncompress",
		"is_start" : false,
		"name" : file,
	}
	WebSocketSend(&message)
}

// FIXME: Update to kill the process first
func uninstall(data map[string]interface{}) {
	switch data["program"].(string) {
		case "VirtualCloneDrive":
			// nothing ...
		case "NullDC":
			os.RemoveAll("emulators/NullDC")
		case "Demul":
			os.RemoveAll("emulators/Demul")
		case "SSF":
			os.RemoveAll("emulators/SSF_012_beta_R4")
		case "Dolphin":
			os.RemoveAll("emulators/Dolphin-x64")
		case "Mupen64Plus":
			os.RemoveAll("emulators/Mupen64Plus")
		case "PCSX-Reloaded":
			os.RemoveAll("emulators/pcsxr")
		case "PCSX2":
			os.RemoveAll("emulators/pcsx2")
	}
}

func isInstalled(data map[string]interface{}) {
	program := data["program"].(string)

	switch program {
	case "DirectX End User Runtime":
		// Paths on Windows 8.1 X86_32 and X86_64
		check_64_dx10, _ := filepath.Glob("C:/Windows/SysWOW64/d3dx10_*.dll")
		check_64_dx11, _ := filepath.Glob("C:/Windows/SysWOW64/d3dx11_*.dll")
		check_32_dx10, _ := filepath.Glob("C:/Windows/System32/d3dx10_*.dll")
		check_32_dx11, _ := filepath.Glob("C:/Windows/System32/d3dx11_*.dll")
		exist := (len(check_64_dx10) > 0 && len(check_64_dx11) > 0) || 
				(len(check_32_dx10) > 0 && len(check_32_dx11) > 0)
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "DirectX End User Runtime",
		}
		WebSocketSend(&message)
	case "Visual C++ 2010 redist": // msvcr100.dll
		// Paths on Windows 8.1 X86_32 and X86_64
		exist := helpers.PathExists("C:/Windows/SysWOW64/msvcr100.dll") || 
				helpers.PathExists("C:/Windows/System32/msvcr100.dll")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "Visual C++ 2010 redist",
		}
		WebSocketSend(&message)
	case "Visual C++ 2013 redist": // msvcr120.dll
		// Paths on Windows 8.1 X86_32 and X86_64
		exist := helpers.PathExists("C:/Windows/SysWOW64/msvcr120.dll") || 
				helpers.PathExists("C:/Windows/System32/msvcr120.dll")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "Visual C++ 2013 redist",
		}
		WebSocketSend(&message)
	case "7-Zip":
		exist := helpers.PathExists("C:/Program Files/7-Zip/7z.exe") || 
				helpers.PathExists("C:/Program Files (x86)/7-Zip/7z.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "7-Zip",
		}
		WebSocketSend(&message)
	case "VirtualCloneDrive":
		exist := helpers.PathExists("C:/Program Files (x86)/Elaborate Bytes/VirtualCloneDrive/VCDMount.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "VirtualCloneDrive",
		}
		WebSocketSend(&message)
	case "NullDC":
		exist := helpers.PathExists("emulators/NullDC/nullDC_Win32_Release-NoTrace.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "NullDC",
		}
		WebSocketSend(&message)
	case "Demul":
		exist := helpers.PathExists("emulators/Demul/demul.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "Demul",
		}
		WebSocketSend(&message)
	case "SSF":
		exist := helpers.PathExists("emulators/SSF_012_beta_R4/SSF.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "SSF",
		}
		WebSocketSend(&message)
	case "Dolphin":
		exist := helpers.PathExists("emulators/Dolphin-x64/Dolphin.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "Dolphin",
		}
		WebSocketSend(&message)
	case "PCSX-Reloaded":
		exist := helpers.PathExists("emulators/pcsxr/pcsxr.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "PCSX-Reloaded",
		}
		WebSocketSend(&message)
	case "PCSX2":
		exist := helpers.PathExists("emulators/pcsx2/pcsx2.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "PCSX2",
		}
		WebSocketSend(&message)
	case "Mupen 64 Plus":
		exist := helpers.PathExists("emulators/Mupen64Plus/mupen64plus.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "Mupen 64 Plus",
		}
		WebSocketSend(&message)
	default:
		fmt.Printf("Unknown program to check if installed: %s\r\n", program)
	}
}

func httpCB(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, r.URL.Path[1:])
}

func webSocketCB(ws *websocket.Conn) {
	//fmt.Printf("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!webSocketCB\r\n")
	g_websocket_needs_restart = false
	g_ws = ws
	open_files := make(map[string]*os.File)
	buffer := make([]byte, 1024 * 14) // 14 KB buffer

	for ! g_websocket_needs_restart {
		// Read the message
		message_map, err := WebSocketRecieve()
		if err != nil {
			fmt.Printf("Failed to get websocket message: %s\r\n", err)
			return
		}

		fmt.Printf("!!! action: %s\r\n", message_map["action"])

		// Client wants to play a game
		if message_map["action"] == "play" {
			playGame(message_map)

		// Client wants to download a file
		} else if message_map["action"] == "download" {
			downloadFile(message_map)

		// Client wants to know if a file is installed
		} else if message_map["action"] == "is_installed" {
			isInstalled(message_map)

		// Client wants to install a program
		} else if message_map["action"] == "install" {
			install(message_map)

		} else if message_map["action"] == "uninstall" {
			uninstall(message_map)

		} else if message_map["action"] == "set_button_map" {
			setButtonMap(message_map)

		} else if message_map["action"] == "get_button_map" {
			getButtonMap(message_map)

		} else if message_map["action"] == "set_bios" {
			setBios(message_map)

		} else if message_map["action"] == "get_db" {
			getDB()

		} else if message_map["action"] == "set_db" {
			var value map[string]map[string]map[string]interface{} = nil
			var err error = nil

			if message_map["value"] != nil {
				str_value :=  message_map["value"].(string)
				value, err = FromCompressedBase64Json(str_value)
				if err != nil {
					log.Fatal(err)
				}

				setDB(value)
			} else {
				setDB(value)
			}

		} else if message_map["action"] == "get_directx_version" {
			getDirectXVersion()

		} else if message_map["action"] == "set_game_directory" {
			// First try checking if Firefox or Chrome is the foreground window
			hwnd := win32.GetForegroundWindow()
			text := win32.GetWindowText(hwnd)

			// If the focused window is not a known browser, find them manually
			if len(text)==0 || 
				! strings.Contains(text, " - Mozilla Firefox") && 
				! strings.Contains(text, " - Google Chrome") && 
				! strings.Contains(text, " - Opera") && 
				! strings.Contains(text, " - Internet Explorer") {
				// If not, find any Firefox window
				hwnd, text = win32.FindWindowWithTitleText(" - Mozilla Firefox")
				if hwnd < 1 || len(text)==0 {
					// If not, find any Chrome window
					hwnd, text = win32.FindWindowWithTitleText(" - Google Chrome")
					if hwnd < 1 || len(text)==0 {
						// If not, find any Opera window
						hwnd, text = win32.FindWindowWithTitleText(" - Opera")
						if hwnd < 1 || len(text)==0 {
							// If not, find any Internet Explorer window
							hwnd, text = win32.FindWindowWithTitleText(" - Internet Explorer")
							if hwnd < 1 || len(text)==0 {
								// If not, find the Desktop window
								hwnd = win32.GetDesktopWindow()
								text = "Desktop"
							}
						}
					}
				}
			}
			if hwnd < 1 || len(text)==0 {
				log.Fatal("Failed to find any Firefox, Chrome, Opera, Internet Explorer, or the Desktop window to put the Folder Dialog on top of.\r\n")
			}

			// FIXME: How do we pass the string to display?
			browse_info := win32.BROWSEINFO {
				hwnd,
				nil, //desktop_pidl,
				nil,
				nil, // "Select a folder search for games"
				0,
				0,
				0,
				0,
			}
			pidl := win32.SHBrowseForFolder(&browse_info)
			if pidl > 0 {
				message_map["directory_name"] = win32.SHGetPathFromIDList(pidl)
				setGameDirectory(message_map)
			}
		} else if message_map["action"] == "request_get_file" {
			fmt.Printf("websocket request_get_file");
			// Get the file info
			file_name := message_map["file_name"].(string)
			peerid := message_map["peerid"].(string)
			float_pos := message_map["pos"].(float64)
			pos := int64(float_pos)

			// Open the file for reading or get it if already open
			var f *os.File
			if value, ok := open_files[file_name]; ok {
				f = value
			} else {
				f, err = os.Open(file_name)
				if err != nil {
					log.Fatal(err)
				}
				open_files[file_name] = f
			}

			// Get the file size
			fi, err := f.Stat()
			if err != nil {
				log.Fatal(err)
			}
			file_length := fi.Size()

			// Read the next chunk and get the length
			fmt.Printf("pos: %v\r\n", pos)
			_, err = f.Seek(pos, 0)
			if err != nil {
				log.Fatal(err)
			}
			read_len, err := f.Read(buffer)
			if err != nil {
				log.Fatal(err)
			}

			// Send the message
			chunk := buffer[0 : read_len]
			message := map[string]interface{} {
				"action" : "response_get_file",
				"file_name" : file_name,
				"chunk" : chunk,
				"pos" : pos,
				"file_length" : file_length,
				"peerid" : peerid,
			}
			WebSocketSend(message)

		} else if message_map["action"] == "request_has_file" {
			fmt.Printf("websocket request_has_file");
			file_name := message_map["file_name"].(string)
			peerid := message_map["peerid"].(string)
			message := map[string]interface{} {
				"action" : "response_has_file",
				"file_name" : file_name,
				"value" : true,
				"peerid" : peerid,
			}
			WebSocketSend(message)

		// Unknown message from the client
		} else {
			log.Fatal(fmt.Sprintf("Unknown action from client: %s\r\n", message_map["action"]))
		}
	}
	g_websocket_needs_restart = false
	http.Handle("/ws", websocket.Handler(webSocketCB))
}

func uncompress7Zip() {
	// Just return if 7zip already exists
	if helpers.IsFile("7za.exe") {
		return
	}

	// Get a blob of 7zip
	blob := generated.GetCompressed7zip()
	debug.FreeOSMemory()

	// Un Base64 the compressed gob
	zlibed_data, err := base64.StdEncoding.DecodeString(blob)
	blob = ""
	if err != nil {
		log.Fatal(err)
	}
	zlibed_buffer := bytes.NewBuffer([]byte(zlibed_data))
	zlibed_data = zlibed_data[:0]
	debug.FreeOSMemory()

	// Un compress the gob
	var gob_buffer bytes.Buffer
	reader, err := zlib.NewReader(zlibed_buffer)
	if err != nil {
		log.Fatal(err)
	}
	io.Copy(&gob_buffer, reader)
	reader.Close()
	zlibed_buffer.Reset()
	debug.FreeOSMemory()

	// Convert the gob to an array
	var file_data []byte
	decoder := gob.NewDecoder(&gob_buffer)
	err = decoder.Decode(&file_data)
	if err != nil {
		log.Fatal(err)
	}
	gob_buffer.Reset()
	debug.FreeOSMemory()

	// Copy the file_data to an exe
	err = ioutil.WriteFile("7za.exe", file_data, 0644)
	if err != nil {
		log.Fatal(err)
	}
	debug.FreeOSMemory()
}

func UncompressWith7zip(in_file string) {
	// Get the command and arguments
	command := "7za.exe"
	args := []string {
		"x",
		"-y",
		fmt.Sprintf(`%s`, in_file),
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

func useAppDataForStaticFiles() {
	// Make the AppData/Local/emulators-online directory
	app_data := filepath.Join(os.Getenv("USERPROFILE"), "AppData", "Local", "emulators-online")
	fmt.Printf("Storing static files in: %v\r\n", app_data)
	if ! helpers.IsDir(app_data) {
		os.Mkdir(app_data, os.ModeDir)
	}

	// Change to the AppData directory
	os.Chdir(app_data)

	// Make 7za.exe
	uncompress7Zip()

	// Make any directories if they don't exists
	dirs := []string {
		"cache",
		"config",
		"downloads",
		"emulators",
		"images",
		"client",
		"static",
		"client/identify_dreamcast_games",
		"client/identify_playstation2_games",
	}
	for _, dir_name := range dirs {
		if ! helpers.IsDir(dir_name) {
			os.Mkdir(dir_name, os.ModeDir)
		}
	}

	// Get a blob of all the static files
	blob := generated.GetCompressedFiles()
	debug.FreeOSMemory()

	// Un Base64 the compressed gob map
	zlibed_data, err := base64.StdEncoding.DecodeString(blob)
	blob = ""
	if err != nil {
		log.Fatal(err)
	}
	debug.FreeOSMemory()

	// Write the gob to file
	err = ioutil.WriteFile("gob.7z", zlibed_data, 0644)
	if err != nil {
		log.Fatal(err)
	}

	// Uncompress the gob to file
	UncompressWith7zip("gob.7z")

	// Read the gob from file
	file_data, err := ioutil.ReadFile("gob")
	if err != nil {
		log.Fatal(err)
	}
	debug.FreeOSMemory()

	// Convert the gob to the file map
	var file_map map[string][]byte
	buffer := bytes.NewBuffer([]byte(file_data))
	decoder := gob.NewDecoder(buffer)
	err = decoder.Decode(&file_map)
	if err != nil {
		log.Fatal(err)
	}
	buffer.Reset()
	debug.FreeOSMemory()

	// Copy the file_map to files
	// FIXME: This copies the files for each run. Even if they are already there!
	// We need a way to quickly check if the files in the exe are different
    for file_name, data := range file_map {
		//if ! helpers.IsFile(file_name) {
			err := ioutil.WriteFile(file_name, data, 0644)
			if err != nil {
				log.Fatal(err)
			}
		//}
    }

	// Remove the temp files
	os.Remove("gob")
	os.Remove("gob.7z")

	debug.FreeOSMemory()
}

func loadFileModifyDates() {
	// Load the file modify dates
	for _, console := range consoles {
		file_modify_dates[console] = map[string]int64{}
		file_name := fmt.Sprintf("cache/file_modify_dates_%s.json", console)
		if helpers.IsFile(file_name) {
			file_data, err := ioutil.ReadFile(file_name)
			if err != nil {
				log.Fatal(err)
			}
			console_dates := file_modify_dates[console]
			err = json.Unmarshal(file_data, &console_dates)
			if err != nil {
				log.Fatal(err)
			}

			// Remove any non existent files from the modify db
			keys := []string{}
			for k := range file_modify_dates[console] {
				keys = append(keys, k)
			}

			for _, entry := range keys {
				if ! helpers.IsFile(entry) {
					delete(file_modify_dates[console], entry)
				}
			}
		}
	}
}

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	// Set what game consoles to support
	consoles = []string{
		//"gamecube",
		//"nintendo64",
		//"saturn",
		"dreamcast",
		//"playstation1",
		"playstation2",
	}

	// Initialize the globals
	db = make(map[string]map[string]map[string]interface{})
	file_modify_dates = map[string]map[string]int64{}
	long_running_tasks = map[string]LongRunningTask{}

	for _, console := range consoles {
		db[console] = make(map[string]map[string]interface{})
		file_modify_dates[console] = map[string]int64{}
	}

	demul = helpers.NewDemul()
	pcsx2 = helpers.NewPCSX2()

	// Get the websocket port from the args
	var ws_port int64 = 9090
	var err error
	if len(os.Args) >= 2 {
		ws_port, err = strconv.ParseInt(os.Args[1], 10, 0)
		if err != nil {
			log.Fatal(err)
		}
	}

	// If "local" use the static files in the current directory
	// If not use the static files in AppData
	if len(os.Args) < 3 || os.Args[2] != "local" {
		useAppDataForStaticFiles()
	} else {
		// Make 7za.exe
		uncompress7Zip()
	}

	// Get the DirectX Version
	helpers.StartBackgroundSearchForDirectXVersion()

	server_address := fmt.Sprintf("127.0.0.1:%v", ws_port)
	http.Handle("/ws", websocket.Handler(webSocketCB))
	http.HandleFunc("/", httpCB)
	fmt.Printf("Server running at: http://%s\r\n",  server_address)
	err = http.ListenAndServe(server_address, nil)
	if err != nil {
		log.Fatal(err)
	}
}


