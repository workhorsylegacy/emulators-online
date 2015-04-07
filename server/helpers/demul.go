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

import(
	"os"
	"strings"
	"os/exec"
	"bytes"
	"fmt"
	"io/ioutil"
	"path/filepath"
)


var BUTTON_CODE_MAP map[string]int64

// Figure out the DirectX version
var gpu_dll_version string
var directx_version string

type Demul struct {
	BaseConsole
}

// FIXME: How do we run this code when the module is loaded?
func main() {
	BUTTON_CODE_MAP = map[string]int64 {
		"button_12" : 805306368, // up
		"button_13" : 805306369, // down
		"button_14" : 805306370, // left
		"button_15" : 805306371, // right
		"button_9" : 805306372, // start
		"button_0" : 805306380, // A
		"button_1" : 805306381, // B
		"button_2" : 805306382, // X
		"button_3" : 805306383, // Y
		"button_7" : 1342177280, // L Trigger
		"button_6" : 1342177536, // R Trigger
		"axes_0-" : -1879048192, // L Stick Left
		"axes_0+" : -1879047936, // L Stick Right
		"axes_1-" : -1879047680, // L Stick Up
		"axes_1+" : -1879047424, // L Stick Down
		"axes_2-" : -1879047168, // R Stick Left
		"axes_2+" : -1879046912, // R Stick Right
		"axes_3-" : -1879046656, // R Stick Up
		"axes_3+" : -1879046400, // R Stick Down
	}

	// Run the command and wait for it to complete
	cmd := exec.Command("dxdiag.exe", "/t", "directx_info.txt")
	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	if err != nil {
		fmt.Printf("Failed to determine DirectX version: %s\r\n", err)
		return
	}

	data, err := ioutil.ReadFile("directx_info.txt")
	if err != nil {
		fmt.Printf("Failed to determine DirectX version: %s\r\n", err)
		return
	}
	string_data := string(data)
	directx_version := Between(string_data, "DirectX Version: ", "\r\n")

	if strings.Contains(directx_version, "11") {
		gpu_dll_version = "gpuDX11.dll"
	} else if strings.Contains(directx_version, "10") {
		gpu_dll_version = "gpuDX10.dll"
	} else {
		fmt.Printf("Failed to determine DirectX version.\r\n")
		return
	}
}

func (self *Demul) Setup() {
	// FIXME: How do we run the base class constructor?
	//BaseConsole.setup("config/demul.json")

	// Setup the initial map, if there is none
	if self.button_map != nil {
		self.button_map = map[string]string {
			"btn_up_demul" : "",
			"btn_down_demul" : "",
			"btn_left_demul" : "",
			"btn_right_demul" : "",
			"btn_start_demul" : "",
			"btn_a_demul" : "",
			"btn_b_demul" : "",
			"btn_x_demul" : "",
			"btn_y_demul" : "",
			"btn_l_trigger_demul" : "",
			"btn_r_trigger_demul" : "",
			"btn_left_stick_up_demul" : "",
			"btn_left_stick_down_demul" : "",
			"btn_left_stick_left_demul" : "",
			"btn_left_stick_right_demul" : "",
			"btn_right_stick_up_demul" : "",
			"btn_right_stick_down_demul" : "",
			"btn_right_stick_left_demul" : "",
			"btn_right_stick_right_demul" : "",
		}
	}
}

func (self *Demul) IsInstalled() bool {
	return IsDir("emulators/Demul/")
}

func (self *Demul) _setup_pad() {
		config := map[string]map[string]interface{} {
			"JOY0_0" : {
				"UP" : 0,
				"DOWN" : 0,
				"LEFT" : 0,
				"RIGHT" : 0,
				"A" : 0,
				"B" : 0,
				"C" : 0,
				"D" : 0,
				"X" : 0,
				"Y" : 0,
				"Z" : 0,
				"LTRIG" : 0,
				"RTRIG" : 0,
				"START" : 0,
				"S1UP" : 0,
				"S1DOWN" : 0,
				"S1LEFT" : 0,
				"S1RIGHT" : 0,
				"S2UP" : 0,
				"S2DOWN" : 0,
				"S2LEFT" : 0,
				"S2RIGHT" : 0,
			},
			"JOY0_1" : {
				"UP" : 0,
				"DOWN" : 0,
				"LEFT" : 0,
				"RIGHT" : 0,
				"A" : 0,
				"B" : 0,
				"C" : 0,
				"D" : 0,
				"X" : 0,
				"Y" : 0,
				"Z" : 0,
				"LTRIG" : 0,
				"RTRIG" : 0,
				"START" : 0,
				"S1UP" : 0,
				"S1DOWN" : 0,
				"S1LEFT" : 0,
				"S1RIGHT" : 0,
				"S2UP" : 0,
				"S2DOWN" : 0,
				"S2LEFT" : 0,
				"S2RIGHT" : 0,
			},
			"JOY0_2" : {
				"UP" : 0,
				"DOWN" : 0,
				"LEFT" : 0,
				"RIGHT" : 0,
				"A" : 0,
				"B" : 0,
				"C" : 0,
				"D" : 0,
				"X" : 0,
				"Y" : 0,
				"Z" : 0,
				"LTRIG" : 0,
				"RTRIG" : 0,
				"START" : 0,
				"S1UP" : 0,
				"S1DOWN" : 0,
				"S1LEFT" : 0,
				"S1RIGHT" : 0,
				"S2UP" : 0,
				"S2DOWN" : 0,
				"S2LEFT" : 0,
				"S2RIGHT" : 0,
			},
			"JOY0_3" : {
				"UP" : 0,
				"DOWN" : 0,
				"LEFT" : 0,
				"RIGHT" : 0,
				"A" : 0,
				"B" : 0,
				"C" : 0,
				"D" : 0,
				"X" : 0,
				"Y" : 0,
				"Z" : 0,
				"LTRIG" : 0,
				"RTRIG" : 0,
				"START" : 0,
				"S1UP" : 0,
				"S1DOWN" : 0,
				"S1LEFT" : 0,
				"S1RIGHT" : 0,
				"S2UP" : 0,
				"S2DOWN" : 0,
				"S2LEFT" : 0,
				"S2RIGHT" : 0,
			},
			"JAMMA0_0" : {
				"PUSH1" : 0,
				"PUSH2" : 0,
				"PUSH3" : 0,
				"PUSH4" : 0,
				"PUSH5" : 0,
				"PUSH6" : 0,
				"PUSH7" : 0,
				"PUSH8" : 0,
				"SERVICE" : 0,
				"START" : 0,
				"COIN" : 0,
				"DIGITALUP" : 0,
				"DIGITALDOWN" : 0,
				"DIGITALLEFT" : 0,
				"DIGITALRIGHT" : 0,
				"ANALOGUP" : 0,
				"ANALOGDOWN" : 0,
				"ANALOGLEFT" : 0,
				"ANALOGRIGHT" : 0,
				"ANALOGUP2" : 0,
				"ANALOGDOWN2" : 0,
				"ANALOGLEFT2" : 0,
				"ANALOGRIGHT2" : 0,
			},
			"JAMMA0_1" : {
				"PUSH1" : 0,
				"PUSH2" : 0,
				"PUSH3" : 0,
				"PUSH4" : 0,
				"PUSH5" : 0,
				"PUSH6" : 0,
				"PUSH7" : 0,
				"PUSH8" : 0,
				"SERVICE" : 0,
				"START" : 0,
				"COIN" : 0,
				"DIGITALUP" : 0,
				"DIGITALDOWN" : 0,
				"DIGITALLEFT" : 0,
				"DIGITALRIGHT" : 0,
				"ANALOGUP" : 0,
				"ANALOGDOWN" : 0,
				"ANALOGLEFT" : 0,
				"ANALOGRIGHT" : 0,
				"ANALOGUP2" : 0,
				"ANALOGDOWN2" : 0,
				"ANALOGLEFT2" : 0,
				"ANALOGRIGHT2" : 0,
			},
			"JAMMA0_2" : {
				"PUSH1" : 0,
				"PUSH2" : 0,
				"PUSH3" : 0,
				"PUSH4" : 0,
				"PUSH5" : 0,
				"PUSH6" : 0,
				"PUSH7" : 0,
				"PUSH8" : 0,
				"SERVICE" : 0,
				"START" : 0,
				"COIN" : 0,
				"DIGITALUP" : 0,
				"DIGITALDOWN" : 0,
				"DIGITALLEFT" : 0,
				"DIGITALRIGHT" : 0,
				"ANALOGUP" : 0,
				"ANALOGDOWN" : 0,
				"ANALOGLEFT" : 0,
				"ANALOGRIGHT" : 0,
				"ANALOGUP2" : 0,
				"ANALOGDOWN2" : 0,
				"ANALOGLEFT2" : 0,
				"ANALOGRIGHT2" : 0,
			},
			"JAMMA0_3" : {
				"PUSH1" : 0,
				"PUSH2" : 0,
				"PUSH3" : 0,
				"PUSH4" : 0,
				"PUSH5" : 0,
				"PUSH6" : 0,
				"PUSH7" : 0,
				"PUSH8" : 0,
				"SERVICE" : 0,
				"START" : 0,
				"COIN" : 0,
				"DIGITALUP" : 0,
				"DIGITALDOWN" : 0,
				"DIGITALLEFT" : 0,
				"DIGITALRIGHT" : 0,
				"ANALOGUP" : 0,
				"ANALOGDOWN" : 0,
				"ANALOGLEFT" : 0,
				"ANALOGRIGHT" : 0,
				"ANALOGUP2" : 0,
				"ANALOGDOWN2" : 0,
				"ANALOGLEFT2" : 0,
				"ANALOGRIGHT2" : 0,
			},
			"MAHJONG0_0" : {
				"A" : 0,
				"B" : 0,
				"C" : 0,
				"D" : 0,
				"E" : 0,
				"F" : 0,
				"G" : 0,
				"H" : 0,
				"I" : 0,
				"J" : 0,
				"K" : 0,
				"L" : 0,
				"M" : 0,
				"N" : 0,
				"FF" : 0,
				"STR" : 0,
				"BET" : 0,
				"LST" : 0,
				"KAN" : 0,
				"PON" : 0,
				"CHI" : 0,
				"RCH" : 0,
				"RON" : 0,
			},
			"GLOBAL0" : {
				"TEST" : 0,
				"TEST2" : 0,
				"SERVICE" : 0,
				"SAVESTATE" : 0,
				"LOADSTATE" : 0,
				"NEXTSTATE" : 0,
				"PREVSTATE" : 0,
				"DEADZONE" : 0,
			},
			"JOY1_0" : {
				"UP" : 0,
				"DOWN" : 0,
				"LEFT" : 0,
				"RIGHT" : 0,
				"A" : 0,
				"B" : 0,
				"C" : 0,
				"D" : 0,
				"X" : 0,
				"Y" : 0,
				"Z" : 0,
				"LTRIG" : 0,
				"RTRIG" : 0,
				"START" : 0,
				"S1UP" : 0,
				"S1DOWN" : 0,
				"S1LEFT" : 0,
				"S1RIGHT" : 0,
				"S2UP" : 0,
				"S2DOWN" : 0,
				"S2LEFT" : 0,
				"S2RIGHT" : 0,
			},
			"JOY1_1" : {
				"UP" : 0,
				"DOWN" : 0,
				"LEFT" : 0,
				"RIGHT" : 0,
				"A" : 0,
				"B" : 0,
				"C" : 0,
				"D" : 0,
				"X" : 0,
				"Y" : 0,
				"Z" : 0,
				"LTRIG" : 0,
				"RTRIG" : 0,
				"START" : 0,
				"S1UP" : 0,
				"S1DOWN" : 0,
				"S1LEFT" : 0,
				"S1RIGHT" : 0,
				"S2UP" : 0,
				"S2DOWN" : 0,
				"S2LEFT" : 0,
				"S2RIGHT" : 0,
			},
			"JOY1_2" : {
				"UP" : 0,
				"DOWN" : 0,
				"LEFT" : 0,
				"RIGHT" : 0,
				"A" : 0,
				"B" : 0,
				"C" : 0,
				"D" : 0,
				"X" : 0,
				"Y" : 0,
				"Z" : 0,
				"LTRIG" : 0,
				"RTRIG" : 0,
				"START" : 0,
				"S1UP" : 0,
				"S1DOWN" : 0,
				"S1LEFT" : 0,
				"S1RIGHT" : 0,
				"S2UP" : 0,
				"S2DOWN" : 0,
				"S2LEFT" : 0,
				"S2RIGHT" : 0,
			},
			"JOY1_3" : {
				"UP" : 0,
				"DOWN" : 0,
				"LEFT" : 0,
				"RIGHT" : 0,
				"A" : 0,
				"B" : 0,
				"C" : 0,
				"D" : 0,
				"X" : 0,
				"Y" : 0,
				"Z" : 0,
				"LTRIG" : 0,
				"RTRIG" : 0,
				"START" : 0,
				"S1UP" : 0,
				"S1DOWN" : 0,
				"S1LEFT" : 0,
				"S1RIGHT" : 0,
				"S2UP" : 0,
				"S2DOWN" : 0,
				"S2LEFT" : 0,
				"S2RIGHT" : 0,
			},
			"JAMMA1_0" : {
				"PUSH1" : 0,
				"PUSH2" : 0,
				"PUSH3" : 0,
				"PUSH4" : 0,
				"PUSH5" : 0,
				"PUSH6" : 0,
				"PUSH7" : 0,
				"PUSH8" : 0,
				"SERVICE" : 0,
				"START" : 0,
				"COIN" : 0,
				"DIGITALUP" : 0,
				"DIGITALDOWN" : 0,
				"DIGITALLEFT" : 0,
				"DIGITALRIGHT" : 0,
				"ANALOGUP" : 0,
				"ANALOGDOWN" : 0,
				"ANALOGLEFT" : 0,
				"ANALOGRIGHT" : 0,
				"ANALOGUP2" : 0,
				"ANALOGDOWN2" : 0,
				"ANALOGLEFT2" : 0,
				"ANALOGRIGHT2" : 0,
			},
			"JAMMA1_1" : {
				"PUSH1" : 0,
				"PUSH2" : 0,
				"PUSH3" : 0,
				"PUSH4" : 0,
				"PUSH5" : 0,
				"PUSH6" : 0,
				"PUSH7" : 0,
				"PUSH8" : 0,
				"SERVICE" : 0,
				"START" : 0,
				"COIN" : 0,
				"DIGITALUP" : 0,
				"DIGITALDOWN" : 0,
				"DIGITALLEFT" : 0,
				"DIGITALRIGHT" : 0,
				"ANALOGUP" : 0,
				"ANALOGDOWN" : 0,
				"ANALOGLEFT" : 0,
				"ANALOGRIGHT" : 0,
				"ANALOGUP2" : 0,
				"ANALOGDOWN2" : 0,
				"ANALOGLEFT2" : 0,
				"ANALOGRIGHT2" : 0,
			},
			"JAMMA1_2" : {
				"PUSH1" : 0,
				"PUSH2" : 0,
				"PUSH3" : 0,
				"PUSH4" : 0,
				"PUSH5" : 0,
				"PUSH6" : 0,
				"PUSH7" : 0,
				"PUSH8" : 0,
				"SERVICE" : 0,
				"START" : 0,
				"COIN" : 0,
				"DIGITALUP" : 0,
				"DIGITALDOWN" : 0,
				"DIGITALLEFT" : 0,
				"DIGITALRIGHT" : 0,
				"ANALOGUP" : 0,
				"ANALOGDOWN" : 0,
				"ANALOGLEFT" : 0,
				"ANALOGRIGHT" : 0,
				"ANALOGUP2" : 0,
				"ANALOGDOWN2" : 0,
				"ANALOGLEFT2" : 0,
				"ANALOGRIGHT2" : 0,
			},
			"JAMMA1_3" : {
				"PUSH1" : 0,
				"PUSH2" : 0,
				"PUSH3" : 0,
				"PUSH4" : 0,
				"PUSH5" : 0,
				"PUSH6" : 0,
				"PUSH7" : 0,
				"PUSH8" : 0,
				"SERVICE" : 0,
				"START" : 0,
				"COIN" : 0,
				"DIGITALUP" : 0,
				"DIGITALDOWN" : 0,
				"DIGITALLEFT" : 0,
				"DIGITALRIGHT" : 0,
				"ANALOGUP" : 0,
				"ANALOGDOWN" : 0,
				"ANALOGLEFT" : 0,
				"ANALOGRIGHT" : 0,
				"ANALOGUP2" : 0,
				"ANALOGDOWN2" : 0,
				"ANALOGLEFT2" : 0,
				"ANALOGRIGHT2" : 0,
			},
			"MAHJONG01_0" : {
				"A" : 0,
				"B" : 0,
				"C" : 0,
				"D" : 0,
				"E" : 0,
				"F" : 0,
				"G" : 0,
				"H" : 0,
				"I" : 0,
				"J" : 0,
				"K" : 0,
				"L" : 0,
				"M" : 0,
				"N" : 0,
				"FF" : 0,
				"STR" : 0,
				"BET" : 0,
				"LST" : 0,
				"KAN" : 0,
				"PON" : 0,
				"CHI" : 0,
				"RCH" : 0,
				"RON" : 0,
			},
			"GLOBAL1" : {
				"TEST" : 0,
				"TEST2" : 0,
				"SERVICE" : 0,
				"SAVESTATE" : 0,
				"LOADSTATE" : 0,
				"NEXTSTATE" : 0,
				"PREVSTATE" : 0,
				"DEADZONE" : 0,
			},
		}

		// Setup the gamepad
		config["JOY0_0"] = map[string]interface{} {
			"UP" : BUTTON_CODE_MAP[self.button_map["btn_up_demul"]],
			"DOWN" : BUTTON_CODE_MAP[self.button_map["btn_down_demul"]],
			"LEFT" : BUTTON_CODE_MAP[self.button_map["btn_left_demul"]],
			"RIGHT" : BUTTON_CODE_MAP[self.button_map["btn_right_demul"]],
			"A" : BUTTON_CODE_MAP[self.button_map["btn_a_demul"]],
			"B" : BUTTON_CODE_MAP[self.button_map["btn_b_demul"]],
			"C" : 0,
			"D" : 0,
			"X" : BUTTON_CODE_MAP[self.button_map["btn_x_demul"]],
			"Y" : BUTTON_CODE_MAP[self.button_map["btn_y_demul"]],
			"Z" : 0,
			"LTRIG" : BUTTON_CODE_MAP[self.button_map["btn_l_trigger_demul"]],
			"RTRIG" : BUTTON_CODE_MAP[self.button_map["btn_r_trigger_demul"]],
			"START" : BUTTON_CODE_MAP[self.button_map["btn_start_demul"]],
			"S1UP" : BUTTON_CODE_MAP[self.button_map["btn_left_stick_up_demul"]],
			"S1DOWN" : BUTTON_CODE_MAP[self.button_map["btn_left_stick_down_demul"]],
			"S1LEFT" : BUTTON_CODE_MAP[self.button_map["btn_left_stick_left_demul"]],
			"S1RIGHT" : BUTTON_CODE_MAP[self.button_map["btn_left_stick_right_demul"]],
			"S2UP" : BUTTON_CODE_MAP[self.button_map["btn_right_stick_up_demul"]],
			"S2DOWN" : BUTTON_CODE_MAP[self.button_map["btn_right_stick_down_demul"]],
			"S2LEFT" : BUTTON_CODE_MAP[self.button_map["btn_right_stick_left_demul"]],
			"S2RIGHT" : BUTTON_CODE_MAP[self.button_map["btn_right_stick_right_demul"]],
		}

		write_ini_file("emulators/Demul/padDemul.ini", config)
}

func (self *Demul) _setup_spu() {
	config := map[string]map[string]interface{} {
		"main" : {
			"spuDisable" : "false",
			"cddaDisable" : "false",
			"dspDisable" : "false",
			"spuRecord" : "false",
			"bufSize" : 2048,
		},
	}
	write_ini_file("emulators/Demul/spuDemul.ini", config)
}

func (self *Demul) _setup_net() {
	config := map[string]map[string]interface{} {
		"main" : {
			"netEnable" : "false",
			"swapDisable" : "false",
			"NameOverride" : "",
		},
	}
	write_ini_file("emulators/Demul/netDemul.ini", config)
}

func (self *Demul) _setup_gdr() {
		config := map[string]map[string]interface{} {
			"main" : {
				"imageFileName" : "",
				"openDialog" : "true",
			},
		}
		write_ini_file("emulators/Demul/gdrImage.ini", config)
}

func (self *Demul) _setup_directx() {
		// Setup DirectX
		config := map[string]map[string]interface{} {
			"main" : {
				"Vsync" : 0,
				"AutoSort" : 0,
				"NetworkSort" : 0,
				"OModifier" : 0,
				"TModifier" : 0,
				"UseFullscreen" : 0,
				"rotate" : 0,
				"aspect" : 1,
				"scaling" : 1,
				"MaxLayers" : 32,
				"NotAutoRotate" : 0,
			},
			"resolution" : {
				"Width" : 640,
				"Height" : 480,
			},
			"shaders" : {
				"usePass1" : 0,
				"usePass2" : 0,
				"shaderPass1" : "",
				"shaderPass2" : "",
			},
		}

		if strings.Contains(directx_version, "11") {
			write_ini_file("emulators/Demul/gpuDX11.ini", config)
		} else if strings.Contains(directx_version, "10") {
			write_ini_file("emulators/Demul/gpuDX10.ini", config)
		}
}

func (self *Demul) _setup_demul() map[string]map[string]interface{} {
		// Setup Demul
		files_nvram, _ := filepath.Abs("emulators/Demul/nvram/")
		files_roms0, _ := filepath.Abs("emulators/Demul/roms/")
		plugins_directory, _ := filepath.Abs("emulators/Demul/plugins/")
		vms_vmsa0, _ := filepath.Abs("emulators/Demul/memsaves/vms00.bin")

		config := map[string]map[string]interface{} {
			"files" : {
				"nvram" : files_nvram,
				"romsPathsCount" : 1,
				"roms0" : files_roms0,
			},
			"PORTD" : {
				"device" : -1,
				"port4" : -1,
				"port2" : -1,
				"port3" : -1,
				"port0" : -1,
				"port1" : -1,
			},
			"PORTB" : {
				"device" : -1,
				"port4" : -1,
				"port2" : -1,
				"port3" : -1,
				"port0" : -1,
				"port1" : -1,
			},
			"PORTC" : {
				"device" : -1,
				"port4" : -1,
				"port2" : -1,
				"port3" : -1,
				"port0" : -1,
				"port1" : -1,
			},
			"PORTA" : {
				"device" : 16777216,
				"port4" : -1,
				"port2" : -1,
				"port3" : -1,
				"port0" : 234881024,
				"port1" : 65536,
			},
			"plugins" : {
				"gdr" : "gdrImage.dll",
				"spu" : "spuDemul.dll",
				"pad" : "padDemul.dll",
				"directory" : plugins_directory,
				"gpu" : gpu_dll_version,
				"net" : "netDemul.dll",
			},
			"main" : {
				"windowY" : 100,
				"windowX" : 100,
				"VMUscreendisable" : "false",
				"dcBios" : 3,
				"region" : 1,
				"activateBBA" : "false",
				"cpumode" : 1,
				"hikaruBios" : 1,
				"naomiBiosAuto" : "true",
				"broadcast" : 1,
				"lastEmuRunMode" : 0,
				"naomifreq" : 1,
				"naomiLLEMIE" : "false",
				"timehack" : "true",
				"videomode" : 768,
			},
			"VMS" : {
				"VMSA4" : "",
				"VMSA0" : vms_vmsa0,
				"VMSA1" : "",
				"VMSA2" : "",
				"VMSA3" : "",
				"VMSC2" : "",
				"VMSD4" : "",
				"VMSD0" : "",
				"VMSD2" : "",
				"VMSD1" : "",
				"VMSC3" : "",
				"VMSD3" : "",
				"VMSC0" : "",
				"VMSB4" : "",
				"VMSC4" : "",
				"VMSC1" : "",
				"VMSB1" : "",
				"VMSB0" : "",
				"VMSB3" : "",
				"VMSB2" : "",
			},
		}
		write_ini_file("emulators/Demul/Demul.ini", config)
		return config
}

func (self *Demul) Run(path string, binary string, on_stop func(memory_card []byte)) {
	// Setup ini files
	self._setup_spu()
	self._setup_pad()
	self._setup_net()
	self._setup_gdr()
	self._setup_directx()
	config := self._setup_demul()

	// Get the window title
	directx_dll := config["plugins"]["gpu"]
	var window_name string
	if path=="" && binary=="" {
		window_name = "Demul"
	} else if directx_dll == "gpuDX11.dll" {
		window_name = "gpuDX11"
	} else if directx_dll == "gpuDX10.dll" {
		window_name = "gpuDX10"
	}

	os.Chdir("emulators/Demul/")

	// Figure out if running a game or not
	var command CommandWithArgs
	full_screen := false
	if binary != "" {
		name := "demul.exe"
		args := []string {"-run=dc", fmt.Sprintf("-image='%s'", binary)}
		command = CommandWithArgs {name, args}
		full_screen = true
	} else {
		name := "demul.exe"
		args := []string {"-run=dc"}
		command = CommandWithArgs {name, args}
		full_screen = false
	}

	// Run the game
	var runner EmuRunner
	full_screen_alt_enter := true
	runner.Setup(command, window_name, full_screen, full_screen_alt_enter)
	runner.Run()
	os.Chdir("../..")

	// Upload the memory card to the server
	if on_stop != nil {
		memory_card, _ := ioutil.ReadFile("emulators/Demul/memsaves/vms00.bin")
		on_stop(memory_card)
	}
}
