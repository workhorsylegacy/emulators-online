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

package main

import (
	"fmt"
	"strings"
	//"io"
	"io/ioutil"
	"path/filepath"
	"os"
	"errors"
	"runtime"
	"log"
	"os/exec"
	"compress/zlib"
	//"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"bytes"
	"strconv"
	//"io"
	"math"

	"net/http"
	"golang.org/x/net/websocket"

	"emu_archive/server/helpers"
	//from identify_playstation2_games import *
)


type LongRunningTask struct {
	thread int
	percentage float64
}

type EmuRunner struct {}
//type Demul struct {}
//type Dolphin struct {}
//type SSF struct {}
//type Mupen64Plus struct {}
//type PCSXR struct {}
//type PCSX2 struct {}

var db map[string]map[string]map[string]interface{}
var file_modify_dates map[string]map[string]int64
var long_running_tasks map[string]LongRunningTask
var runner EmuRunner
//var demul Demul
//var dolphin Dolphin
//var ssf SSF
//var mupen64plus Mupen64Plus
//var pcsxr PCSXR
//var pcsx2 PCSX2


func Round(f float64) float64 {
	return math.Floor(f + .5)
}

func RoundPlus(f float64, places int) (float64) {
	shift := math.Pow(10, float64(places))
	return Round(f * shift) / shift;
}

func clean_path(file_path string) string {
	//file_path = filepath.Abs(file_path)
	new_path := strings.Replace(file_path, "\\", "/", -1)
	//new_path = new_path.replace(": ", " - ").replace("/", "+")
	return new_path
}

func abs_path(file_path string) string {
	file_path, _ = filepath.Abs(file_path)
	file_path = strings.Replace(file_path, "\\", "/", -1)
	//file_path  = strings.Replace(strings.Replace(file_path, ": ", " - ", -1), "/", "+", -1)
	return file_path
}

func web_socket_send(ws *websocket.Conn, thing interface{}) error {
	//fmt.Printf("web_socket_send ????????????????????????????????????????\r\n")

	// Convert the object to base64ed json
	message, err := to_b64_json(thing)
	if err != nil {
		fmt.Printf("Failed to write web socket message: %s\r\n", err)
		//ws.Close()
		return err
	}
	//fmt.Printf("message: %s\r\n", message)

	// Get the header
	whole_message := fmt.Sprintf("%d:%s", len(message), message)
	//fmt.Printf("whole_message: %s\r\n", whole_message)

	// Write the message
	buffer := []byte(whole_message)
	write_len, err := ws.Write(buffer)
	if err != nil {
		fmt.Printf("Failed to write web socket message: %s\r\n", err)
		//ws.Close()
		return err
	}
	if write_len != len(buffer) {
		return errors.New("Whole buffer was not written to web socket\r\n")
	}
	//fmt.Printf("write_len: %d\r\n", write_len)

	return nil
}

func web_socket_recieve(ws *websocket.Conn) (map[string]string, error) {
	//fmt.Printf("web_socket_recieve ???????????????????????????????????\r\n")
	buffer := make([]byte, 20)

	// Read the message header
	read_len, err := ws.Read(buffer)
	if err != nil {
		fmt.Printf("Failed to read web socket message: %s\r\n", err)
		//ws.Close()
		return nil, err
	}
	//fmt.Printf("read_len: %d\r\n", read_len)

	// Get the message length
	message := string(buffer[0 : read_len])
	chunks := strings.Split(message, ":")
	message_length64, _ := strconv.ParseInt(chunks[0], 10, 0)
	message_length := int(message_length64)
	message = chunks[1]

	// Read the rest of the message
	buffer = make([]byte, message_length)
	read_len, err = ws.Read(buffer)
	if err != nil {
		fmt.Printf("Failed to read web socket message: %s\r\n", err)
		//ws.Close()
		return nil, err
	}
	//fmt.Printf("read_len: %d\r\n", read_len)
	message = message + string(buffer[0 : read_len])

	// Convert the message from base64 and json
	thing, err := from_b64_json(message)
	if err != nil {
		fmt.Printf("Failed to decode web socket message: %s\r\n", err)
		//ws.Close()
		return nil, err
	}

	//fmt.Printf("thing: %s\r\n", thing)
	return thing, nil
}

func from_b64_json(message string) (map[string]string, error) {
	var retval map[string]string

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

func to_b64_json(thing interface{}) (string, error) {
	// Convert the object to json
	jsoned_data, err := json.Marshal(thing)
	if err != nil {
		return "", err
	}
	//stringed_data := string(jsoned_data)

	// Convert the jsoned object to base64
	b64ed_data := base64.StdEncoding.EncodeToString(jsoned_data)
	if err != nil {
		return "", err
	}
	b64ed_and_jsoned_data := string(b64ed_data)

	return b64ed_and_jsoned_data, err
}

func is_long_running_task(task_name string) bool {
	_, ok := long_running_tasks[task_name]
	return ok
}

func remove_long_running_task(ws *websocket.Conn, task_name string) {
	// Remove the task
	if _, ok := long_running_tasks[task_name]; ok {
		delete(long_running_tasks, task_name)
	}

	// Get a list of the threads and their percentages
	var task_and_percentages map[string]float64
	for name, long_running_task := range long_running_tasks {
		task_and_percentages[name] = long_running_task.percentage
	}

	json_data, _ := to_b64_json(task_and_percentages)
	message := map[string]string {
		"action" : "long_running_tasks",
		"json_data" : json_data,
	}
	web_socket_send(ws, &message)
}

func add_long_running_task(ws *websocket.Conn, task_name string, thread int) {
	long_running_tasks[task_name] = LongRunningTask {
		thread: thread,
		percentage: 0,
	}

	// Get a list of the threads and their percentages
	var task_and_percentages map[string]float64
	for name, long_running_task := range long_running_tasks {
		task_and_percentages[name] = long_running_task.percentage
	}

	json_data, _ := to_b64_json(task_and_percentages)
	message := map[string]string {
		"action" : "long_running_tasks",
		"json_data" : json_data,
	}
	web_socket_send(ws, &message)
}

func set_long_running_task_percentage(ws *websocket.Conn, task_name string, percentage float64) {
	// Replace the task with one that has an updated percentage
	var old_long_running_task LongRunningTask = long_running_tasks[task_name]
	long_running_tasks[task_name] = LongRunningTask {
		thread: old_long_running_task.thread,
		percentage: percentage,
	}

	// Get a list of the threads and their percentages
	var task_and_percentages map[string]float64
	for name, long_running_task := range long_running_tasks {
		task_and_percentages[name] = long_running_task.percentage
	}

	json_data, _ := to_b64_json(task_and_percentages)
	message := map[string]string {
		"action" : "long_running_tasks",
		"json_data" : json_data,
	}
	web_socket_send(ws, &message)
}

func _get_db(ws *websocket.Conn) {
	fmt.Printf("called _get_db\r\n")

	json_data, _ := to_b64_json(db)
	message := map[string]string {
		"action" : "get_db",
		"json_data" : json_data,
	}
	web_socket_send(ws, message)
}

func _set_bios(data map[string]string) (error) {
	if data["console"] == "dreamcast" {
		// Make the BIOS dir if missing
		if ! helpers.IsDir("emulators/Demul/roms") {
			os.Mkdir("emulators/Demul/roms", os.ModeDir)
		}

		// Get the BIOS file name
		var file_name string
		if data["type"] == "awbios.zip" {
			file_name = "emulators/Demul/roms/awbios.zip"
		} else if data["type"] == "dc.zip" {
			file_name = "emulators/Demul/roms/dc.zip"
		} else if data["type"] == "naomi.zip" {
			file_name = "emulators/Demul/roms/naomi.zip"
		} else if data["type"] == "naomi2.zip" {
			file_name = "emulators/Demul/roms/naomi2.zip"
		}

		// Convert the base64 data to BIOS and write to file
		f, err := os.Open(file_name)
		if err != nil {
			return err
		}
		b642_data, _ := base64.StdEncoding.DecodeString(data["value"])
		f.Write(b642_data)

	} else if data["console"] == "saturn" {
		// Make the BIOS dir if missing
		if ! helpers.IsDir("emulators/SSF_012_beta_R4/bios") {
			os.Mkdir("emulators/SSF_012_beta_R4/bios", os.ModeDir)
		}

		// Get the BIOS file name
		var file_name string
		if data["type"] == "USA" {
			file_name = "emulators/SSF_012_beta_R4/bios/Sega Saturn BIOS (US).bin"
		} else if data["type"] == "EUR" {
			file_name = "emulators/SSF_012_beta_R4/bios/Sega Saturn BIOS (EUR).bin"
		} else if data["type"] == "JAP" {
			file_name = "emulators/SSF_012_beta_R4/bios/Sega Saturn BIOS (JAP).bin"
		}

		// Convert the base64 data to BIOS and write to file
		f, err := os.Open(file_name)
		if err != nil {
			return err
		}
		b642_data, _ := base64.StdEncoding.DecodeString(data["value"])
		f.Write(b642_data)
	}

	return nil
}

func _set_button_map(ws *websocket.Conn, data map[string]string)  {
	if data["console"] == "gamecube" {
		//dolphin.set_button_map(data["value"])

	} else if data["console"] == "nintendo64" {
		//mupen64plus.set_button_map(data["value"])

	} else if data["console"] == "saturn" {
		//ssf.set_button_map(data["value"])

	} else if data["console"] == "dreamcast" {
		//demul.set_button_map(data["value"])

	} else if data["console"] == "Playstation" {
		//pcsxr.set_button_map(data["value"])

	} else if data["console"] == "playstation2" {
		//pcsx2.set_button_map(data["value"])
	}
}

func _get_button_map(ws *websocket.Conn, data map[string]string) {
	var value map[string]string

	if data["console"] == "gamecube" {
		//value = dolphin.get_button_map()

	} else if data["console"] == "nintendo64" {
		//value = mupen64plus.get_button_map()

	} else if data["console"] == "saturn" {
		//value = ssf.get_button_map()

	} else if data["console"] == "dreamcast" {
		//value = demul.get_button_map()

	} else if data["console"] == "Playstation" {
		//value = pcsxr.get_button_map()

	} else if data["console"] == "playstation2" {
		//value = pcsx2.get_button_map()
	}

	message := map[string]interface{} {
		"action" : "get_button_map",
		"value" : value,
		"console" : data["console"],
	}
	web_socket_send(ws, &message)
}

func task(ws *websocket.Conn, data map[string]string) error {
	directory_name := data["directory_name"]
	console := data["console"]

	// Add the thread to the list of long running tasks
	add_long_running_task(ws, fmt.Sprintf("Searching for %s games", console), 5)

	// Get the path for this console
	var path_prefix string
	if console == "gamecube" {
		path_prefix = "games/Nintendo/GameCube"
	} else if console == "nintendo64" {
		path_prefix = "games/Nintendo/Nintendo64"
	} else if console == "saturn" {
		path_prefix = "games/Sega/Saturn"
	} else if console == "dreamcast" {
		path_prefix = "games/Sega/Dreamcast"
	} else if console == "playstation1" {
		path_prefix = "games/Sony/Playstation1"
	} else if console == "playstation2" {
		path_prefix = "games/Sony/Playstation2"
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
		set_long_running_task_percentage(ws, fmt.Sprintf("Searching for %s games", console), percentage)
		done_files += 1.0

		// Skip if the the entry is not a file
		if ! helpers.IsFile(entry) {
			return nil
		}

		// Skip if the game file has not been modified
		var old_modify_date int64 = 0
		if val, ok := file_modify_dates[console][entry]; ok {
			old_modify_date = val // file_modify_dates[console][entry]
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

		// Skip if the file is not the right kind for this console
		if console == "dreamcast" {
			if ! helpers.IsDreamcastFile(entry) {
				return nil
			}
		//} else if console == "playstation2" {
		//	if ! is_playstation2_file(entry) {
		//		return nil
		//	}
		} else {
			log.Fatal(fmt.Sprintf("Unexpected console: %s", console))
		}

		// Get the game info
		var info map[string]string
		if console == "dreamcast" {
			info, err = helpers.GetDreamcastGameInfo(entry)
		//} else if console == "playstation2" {
		//	info, err = get_playstation2_game_info(entry)
		} else {
			log.Fatal(fmt.Sprintf("Unexpected console: %s", console))
		}
		if err != nil {
			fmt.Printf("Failed to find info for game \"%s\"", entry)
			return nil
		}
		fmt.Printf("getting game info: %s", info["title"])
		info["file"] = entry

		// Save the info in the db
		if info != nil {
			title := info["title"]
			clean_title := strings.Replace(strings.Replace(title, ": ", " - ", -1), "/", "+", -1)
			db[console][title] = map[string]interface{} {
				"path" : clean_path(fmt.Sprintf("%s/%s/", path_prefix, clean_title)),
				"binary" : abs_path(info["file"]),
				"bios" : "",
				"images" : []string{},
				"developer" : "", //info["developer"],
				"genre" : "", //info["genre"],
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

	f, err := os.Open(fmt.Sprintf("cache/game_db_%s.json", console))
	if err != nil {
		return err
	}
	jsoned_data, _ := json.Marshal(data["value"])
	f.Write(jsoned_data)

	f, err = os.Open(fmt.Sprintf("cache/file_modify_dates_%s.json", console))
	if err != nil {
		return err
	}
	jsoned_data, _ = json.Marshal(data["value"])
	f.Write(jsoned_data)

	fmt.Printf("Done getting games from directory.\r\n")

	remove_long_running_task(ws, fmt.Sprintf("Searching for %s games", console))

	return nil
}

func _set_game_directory(ws *websocket.Conn, data map[string]string) {
	// Just return if already a long running "Searching for dreamcast games" task
	if is_long_running_task(fmt.Sprintf("Searching for %s games", data["console"])) {
		return
	}

	// FIXME: This function should run in its own thread
	go task(ws, data)

	// Run the task in a thread
	//thread = threading.Thread(target = task, args = (self, data))
	//thread.daemon = true
	//thread.start()
}

func _save_memory_card_cb(memory_card string) {
	var out_buffer bytes.Buffer
	writer := zlib.NewWriter(&out_buffer)
	writer.Write([]byte(memory_card))
	writer.Close()
	// FIXME: Send the memory card to the server
	fmt.Printf("FIXME: Memory card needs saving. length %s\r\n", out_buffer.Len())
}

func _play_game(ws *websocket.Conn, data map[string]string) {
	if data["console"] == "gamecube" {
		//dolphin.run(data["path"], data["binary"])
		//self.log("playing")
		print("Running Dolphin ...")

	} else if data["console"] == "nintendo64" {
		//mupen64plus.run(data["path"], data["binary"])
		//self.log("playing")
		print("Running Mupen64plus ...")

	} else if data["console"] == "saturn" {
		//ssf.run(data["path"], data["binary"], data["bios"])
		//self.log("playing")
		print("Running SSF ...")

	} else if data["console"] == "dreamcast" {
		//demul.run(data["path"], data["binary"], _save_memory_card_cb)
		//self.log("playing")
		print("Running Demul ...")

	} else if data["console"] == "Playstation" {
		//pcsxr.run(data["path"], data["binary"])
		//self.log("playing")
		print("Running PCSX-Reloaded ...")

	} else if data["console"] == "playstation2" {
		//pcsx2.run(data["path"], data["binary"])
		//self.log("playing")
		print("Running PCSX2 ...")
	}
}

func progress_cb(name string, ws *websocket.Conn, progress float64) {
	message := map[string]interface{} {
		"action" : "progress",
		"value" : progress,
		"name" : name,
	}
	web_socket_send(ws, &message)
}

func _download_file(ws *websocket.Conn, data map[string]string) {
	// Get all the info we need
	file_name := data["file"]
	url := data["url"]
	directory := data["dir"]
	name := data["name"]

	// Download the file header
	resp, err := http.Get(url)
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
		progress := RoundPlus((total_length / content_length) * 100.0, 2)
		progress_cb(name, ws, progress)

		// Exit the loop if the file is done
		if EOF || total_length == content_length {
			break
		}
	}
}

func _install(ws *websocket.Conn, data map[string]string) {
	// Start uncompressing
	message := map[string]interface{}{
		"action" : "uncompress",
		"is_start" : true,
		"name" : data["file"],
	}
	web_socket_send(ws, &message)

	if data["file"] == "SetupVirtualCloneDrive.exe" {
		os.Chdir(data["dir"])
		//proc = subprocess.Popen([data["file"], "/S"], stdout=subprocess.PIPE, shell=true) // Silent install
		//proc.communicate()
		cmd := exec.Command(data["file"], "/S")
		var out bytes.Buffer
		cmd.Stdout = &out
		cmd.Run()
		os.Chdir("..")
	} else if data["file"] == "7z920.exe" {
		os.Chdir(data["dir"])
		//proc = subprocess.Popen([data["file"], "/S"], stdout=subprocess.PIPE, shell=true) // Silent install
		//proc.communicate()
		cmd := exec.Command(data["file"], "/S")
		var out bytes.Buffer
		cmd.Stdout = &out
		cmd.Run()
		os.Chdir("..")
	} else if data["file"] == "nullDC_104_r136.7z" {
		wrap := helpers.Wrap7zip{}
		helpers.Setup(&wrap)
		helpers.Uncompress(&wrap, filepath.Join(data["dir"], "nullDC_104_r136.7z"), "emulators/NullDC")
	} else if data["file"] == "demul0582.rar" {
		wrap := helpers.Wrap7zip{}
		helpers.Setup(&wrap)
		helpers.Uncompress(&wrap, filepath.Join(data["dir"], "demul0582.rar"), "emulators/Demul")
	} else if data["file"] == "SSF_012_beta_R4.zip" {
		wrap := helpers.Wrap7zip{}
		helpers.Setup(&wrap)
		helpers.Uncompress(&wrap, filepath.Join(data["dir"], "SSF_012_beta_R4.zip"), "emulators")
	} else if data["file"] == "dolphin-master-4.0-5363-x64.7z" {
		wrap := helpers.Wrap7zip{}
		helpers.Setup(&wrap)
		helpers.Uncompress(&wrap, filepath.Join(data["dir"], "dolphin-master-4.0-5363-x64.7z"), "emulators")
	} else if data["file"] == "mupen64plus-bundle-win32-2.0.zip" {
		wrap := helpers.Wrap7zip{}
		helpers.Setup(&wrap)
		helpers.Uncompress(&wrap, filepath.Join(data["dir"], "mupen64plus-bundle-win32-2.0.zip"), "emulators/Mupen64Plus")
	} else if data["file"] == "pcsxr-1.9.93-win32.zip" {
		wrap := helpers.Wrap7zip{}
		helpers.Setup(&wrap)
		helpers.Uncompress(&wrap, filepath.Join(data["dir"], "pcsxr-1.9.93-win32.zip"), "emulators")
	} else if data["file"] == "pcsx2-v1.3.1-8-gf88bea5-windows-x86.7z" {
		wrap := helpers.Wrap7zip{}
		helpers.Setup(&wrap)
		helpers.Uncompress(&wrap, filepath.Join(data["dir"], "pcsx2-v1.3.1-8-gf88bea5-windows-x86.7z"), "emulators")
	}

	// End uncompressing
	message = map[string]interface{}{
		"action" : "uncompress",
		"is_start" : false,
		"name" : data["file"],
	}
	web_socket_send(ws, &message)
}

func _uninstall(ws *websocket.Conn, data map[string]string) {
	if data["program"] == "VirtualCloneDrive" {
		// nothing ...
	} else if data["program"] == "NullDC" {
		os.RemoveAll("emulators/NullDC")
	} else if data["program"] == "Demul" {
		os.RemoveAll("emulators/Demul")
	} else if data["program"] == "SSF" {
		os.RemoveAll("emulators/SSF_012_beta_R4")
	} else if data["program"] == "Dolphin" {
		os.RemoveAll("emulators/Dolphin-x64")
	} else if data["program"] == "Mupen64Plus" {
		os.RemoveAll("emulators/Mupen64Plus")
	} else if data["program"] == "PCSX-Reloaded" {
		os.RemoveAll("emulators/pcsxr")
	} else if data["program"] == "PCSX2" {
		os.RemoveAll("emulators/pcsx2")
	}
}

func _is_installed(ws *websocket.Conn, data map[string]string) {
	if data["program"] == "DirectX End User Runtime" {
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
		web_socket_send(ws, &message)
	} else if data["program"] == "Visual C++ 2010 redist" { // msvcr100.dll
		// Paths on Windows 8.1 X86_32 and X86_64
		exist := helpers.PathExists("C:/Windows/SysWOW64/msvcr100.dll") || 
				helpers.PathExists("C:/Windows/System32/msvcr100.dll")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "Visual C++ 2010 redist",
		}
		web_socket_send(ws, &message)
	} else if data["program"] == "Visual C++ 2013 redist" { // msvcr120.dll
		// Paths on Windows 8.1 X86_32 and X86_64
		exist := helpers.PathExists("C:/Windows/SysWOW64/msvcr120.dll") || 
				helpers.PathExists("C:/Windows/System32/msvcr120.dll")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "Visual C++ 2013 redist",
		}
		web_socket_send(ws, &message)
	} else if data["program"] == "7-Zip" {
		exist := helpers.PathExists("C:/Program Files/7-Zip/7z.exe") || 
				helpers.PathExists("C:/Program Files (x86)/7-Zip/7z.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "7-Zip",
		}
		web_socket_send(ws, &message)
	} else if data["program"] == "VirtualCloneDrive" {
		exist := helpers.PathExists("C:/Program Files (x86)/Elaborate Bytes/VirtualCloneDrive/VCDMount.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "VirtualCloneDrive",
		}
		web_socket_send(ws, &message)
	} else if data["program"] == "NullDC" {
		exist := helpers.PathExists("emulators/NullDC/nullDC_Win32_Release-NoTrace.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "NullDC",
		}
		web_socket_send(ws, &message)
	} else if data["program"] == "Demul" {
		exist := helpers.PathExists("emulators/Demul/demul.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "Demul",
		}
		web_socket_send(ws, &message)
	} else if data["program"] == "SSF" {
		exist := helpers.PathExists("emulators/SSF_012_beta_R4/SSF.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "SSF",
		}
		web_socket_send(ws, &message)
	} else if data["program"] == "Dolphin" {
		exist := helpers.PathExists("emulators/Dolphin-x64/Dolphin.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "Dolphin",
		}
		web_socket_send(ws, &message)
	} else if data["program"] == "PCSX-Reloaded" {
		exist := helpers.PathExists("emulators/pcsxr/pcsxr.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "PCSX-Reloaded",
		}
		web_socket_send(ws, &message)
	} else if data["program"] == "PCSX2" {
		exist := helpers.PathExists("emulators/pcsx2/pcsx2.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "PCSX2",
		}
		web_socket_send(ws, &message)
	} else if data["program"] == "Mupen 64 Plus" {
		exist := helpers.PathExists("emulators/Mupen64Plus/mupen64plus.exe")
		message := map[string]interface{} {
			"action" : "is_installed",
			"value" : exist,
			"name" : "Mupen 64 Plus",
		}
		web_socket_send(ws, &message)
	} else {
		fmt.Printf("Unknown program to check if installed: %s\r\n", data["program"])
	}
}

/*
class EmuDownloader(downloader.Downloader):
	func __init__(self, server, progress_cb, name, url, file_name, dir_name):
		super(EmuDownloader, self).__init__(url, file_name, dir_name)
		self.server = server
		self.progress_cb = progress_cb
		self.name = name

	func _cb_dl_progress(self, file_name, chunk, data_length, chunk_size, content_length, percent):
		self.progress_cb(self.name, self.server, percent)
*/

func http_cb(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, r.URL.Path[1:])
}

func web_socket_cb(ws *websocket.Conn) {
	//fmt.Printf("web_socket_cb !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\r\n")

	for {
		// Read the message
		message_map, err := web_socket_recieve(ws)
		if err != nil {
			fmt.Printf("Failed to get web socket message: %s\r\n", err)
			//ws.Close()
			return
		}

		// Client wants to play a game
		if message_map["action"] == "play" {
			_play_game(ws, message_map)

		// Client wants to download a file
		} else if message_map["action"] == "download" {
			_download_file(ws, message_map)

		// Client wants to know if a file is installed
		} else if message_map["action"] == "is_installed" {
			_is_installed(ws, message_map)

		// Client wants to install a program
		} else if message_map["action"] == "install" {
			_install(ws, message_map)

		} else if message_map["action"] == "uninstall" {
			_uninstall(ws, message_map)

		} else if message_map["action"] == "set_button_map" {
			_set_button_map(ws, message_map)

		} else if message_map["action"] == "get_button_map" {
			_get_button_map(ws, message_map)

		} else if message_map["action"] == "set_bios" {
			_set_bios(message_map)

		} else if message_map["action"] == "get_db" {
			_get_db(ws)

		} else if message_map["action"] == "set_game_directory" {
/*
			hwnd, text = nil, nil
			func findWindowWithTitleText(title_text):
				// Get the handles of all the windows
				res = []
				func callback(hwnd, arg):
					res.append(hwnd)
					text = win32gui.GetWindowText(hwnd)
				win32gui.EnumWindows(callback, 0)

				// Find the window with the desired title bar text
				for hwnd in res:
					text = win32gui.GetWindowText(hwnd)
					if title_text in text:
						return(hwnd, text)
				return (nil, nil)

			// First try checking if Firefox or Chrome is the foreground window
			hwnd = win32gui.GetForegroundWindow()
			text = win32gui.GetWindowText(hwnd)

			// If the focused window is not Chrome or Firefox, find them manually
			if not text or " - Mozilla Firefox" not in text and " - Google Chrome" not in text and " - Internet Explorer" not in text:
				// If not, find any Firefox window
				hwnd, text = findWindowWithTitleText(" - Mozilla Firefox")
				if not hwnd or not text:
					// If not, find any Chrome window
					hwnd, text = findWindowWithTitleText(" - Google Chrome")
					if not hwnd or not text:
						// If not, find any Internet Explorer window
						hwnd, text = findWindowWithTitleText(" - Internet Explorer")
						if not hwnd or not text:
							// If not, find the Desktop window
							hwnd = win32gui.GetDesktopWindow()
							text = "Desktop"
			if not hwnd or not text:
				print("Failed to find any Firefox, Chrome, Internet Explorer, or the Desktop window to put the Folder Dialog on top of.")
				sys.exit(1)

			desktop_pidl = win32com.shell.shell.SHGetFolderLocation(0, win32com.shell.shellcon.CSIDL_DESKTOP, 0, 0)
			pidl, display_name, image_list = win32com.shell.shell.SHBrowseForFolder(
				hwnd,
				desktop_pidl,
				"Select a folder search for games",
				0,
				nil,
				nil
			)
			if pidl:
				message_map["directory_name"] = win32com.shell.shell.SHGetPathFromIDList(pidl).decode("utf-8")
				_set_game_directory(message_map)
*/
		// Unknown message from the client
		} else {
			log.Fatal(fmt.Sprintf("Unknown action from client: %s", message_map["action"]))
		}
	}
	//ws.Close()
}


func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	//db = map[string]map[string]map[string]interface{}
	file_modify_dates = map[string]map[string]int64{}

	// Move to the main emu_archive directory no matter what path we are launched from
	_, root, _, _ := runtime.Caller(0)
	root = filepath.Dir(root)

	/*
	// When running as an exe, generate the files
	import static_files

	// Make the directory structure
	dirs = [
			"config", "cache", "downloads",
			"emulators", "server",
			"static", "games",
			"games/Nintendo/",
			"games/Nintendo/GameCube/",
			"games/Nintendo/Nintendo64/",
			"games/Sega/",
			"games/Sega/Saturn/",
			"games/Sega/Dreamcast/",
			"games/Sony/",
			"games/Sony/Playstation/",
			"games/Sony/Playstation2/"
	]

	for dir in dirs:
		if ! helpers.PathExists(dir):
			os.Mkdir(dir, os.ModeDir)

	// Make the html, css, js, and json files
	files = ["configure.html", "index.html", "static/funcault.css", 
			"static/emu_archive.js", "static/file_uploader.js",
			"static/input.js", "static/web_socket.js",
			"static/jquery-2.1.3.min.js", "static/favicon.ico",
			"db_dreamcast_official_eu.json",
			"db_dreamcast_official_jp.json",
			"db_dreamcast_official_us.json",
			"db_dreamcast_unofficial.json",
			"db_playstation2_official_as.json",
			"db_playstation2_official_au.json",
			"db_playstation2_official_eu.json",
			"db_playstation2_official_jp.json",
			"db_playstation2_official_ko.json",
			"db_playstation2_official_us.json",
			]

	for file in files:
		if ! helpers.IsFile(file):
			with open(file, "wb") as f:
				data = static_files.static_files[file]
				data = base64.b64decode(data)
				f.write(data)
	*/

	// Load the game database
	consoles := []string{
		"gamecube",
		"nintendo64",
		"saturn",
		"dreamcast",
		"playstation1",
		"playstation2",
	}
	for _, console := range consoles {
		//db[console] = map[string]make[string]interface{}

		// Skip if not file
		cache_file := fmt.Sprintf("cache/game_db_%s.json", console)
		if ! helpers.IsFile(cache_file) {
			continue
		}

		file_data, err := ioutil.ReadFile(cache_file)
		if err != nil {
			log.Fatal(err)
		}
		console_games := db[console]
		err = json.Unmarshal(file_data, &console_games)
		if err != nil {
			log.Fatal(err)
		}
		for k, v := range db[console] {
			fmt.Printf("%s : %s\r\n", k, v)
		}

		// Remove any non existent files
		keys := make([]string, len(db[console]))
		for _, name := range keys {
			data := db[console][name]
			if helpers.IsFile(data["binary"].(string)) {
				delete(db[console], name)
			}
		}
	}

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
				// sys.stderr.write("The file is not valid json "{0}"\r\n".format(file_name))
			}

			// Remove any non existent files from the modify db
			keys := make([]string, len(file_modify_dates[console]))
			for _, entry := range keys {
				if helpers.IsFile(entry) {
					delete(file_modify_dates[console], entry)
				}
			}
		}
	}

	//icon := "static/favicon.ico"
	//hover_text := "Emu Archive"
	//server = nil
	//port := 8080
	//ws_port := 9090
	//server_thread = nil

	server_address := "127.0.0.1:9090"
	http.Handle("/ws", websocket.Handler(web_socket_cb))
	http.HandleFunc("/", http_cb)
	//http.HandleFunc("/configure.html", http_cb)
	//http.Handle("/(.*)", http.FileServer(http.Dir(".")))
	fmt.Printf("Server running at: http://%s\r\n",  server_address)
	http.ListenAndServe(server_address, nil)
}


