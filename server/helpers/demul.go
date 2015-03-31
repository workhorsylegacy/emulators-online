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
/*
import os, sys
import subprocess

import ini
import emu_runner
import base_console


BUTTON_CODE_MAP = {
	'button_12' : 805306368, // up
	'button_13' : 805306369, // down
	'button_14' : 805306370, // left
	'button_15' : 805306371, // right
	'button_9' : 805306372, // start
	'button_0' : 805306380, // A
	'button_1' : 805306381, // B
	'button_2' : 805306382, // X
	'button_3' : 805306383, // Y
	'button_7' : 1342177280, // L Trigger
	'button_6' : 1342177536, // R Trigger
	'axes_0-' : -1879048192, // L Stick Left
	'axes_0+' : -1879047936, // L Stick Right
	'axes_1-' : -1879047680, // L Stick Up
	'axes_1+' : -1879047424, // L Stick Down
	'axes_2-' : -1879047168, // R Stick Left
	'axes_2+' : -1879046912, // R Stick Right
	'axes_3-' : -1879046656, // R Stick Up
	'axes_3+' : -1879046400, // R Stick Down
	None : ''
}

// Figure out the DirectX version
gpu_dll_version = None
directx_version = None
retcode = subprocess.call(["dxdiag.exe", "/t", "directx_info.txt"], shell=True)
if retcode == 0:
	with open("directx_info.txt", 'r') as f:
		data = f.read()
	directx_version = data.split("DirectX Version: ")[1].split("\r\n")[0]

	if '11' in directx_version:
		gpu_dll_version = 'gpuDX11.dll'
	elif '10' in directx_version:
		gpu_dll_version = 'gpuDX10.dll'
	else:
		raise Exception("Failed to determine DirectX version.")
else:
	raise Exception("Failed to determine DirectX version.")


class Demul(base_console.BaseConsole):
	def __init__(self):
		super(Demul, self).__init__('config/demul.json')

		// Setup the initial map, if there is none
		if not self.button_map:
			self.button_map = {
				'btn_up_demul' : None,
				'btn_down_demul' : None,
				'btn_left_demul' : None,
				'btn_right_demul' : None,
				'btn_start_demul' : None,
				'btn_a_demul' : None,
				'btn_b_demul' : None,
				'btn_x_demul' : None,
				'btn_y_demul' : None,
				'btn_l_trigger_demul' : None,
				'btn_r_trigger_demul' : None,
				'btn_left_stick_up_demul' : None,
				'btn_left_stick_down_demul' : None,
				'btn_left_stick_left_demul' : None,
				'btn_left_stick_right_demul' : None,
				'btn_right_stick_up_demul' : None,
				'btn_right_stick_down_demul' : None,
				'btn_right_stick_left_demul' : None,
				'btn_right_stick_right_demul' : None
			}

	def is_installed(self):
		return os.path.isdir('emulators/Demul/')

	def _setup_pad(self):
		global BUTTON_CODE_MAP

		config = {
			'JOY0_0' : {
				'UP' : 0,
				'DOWN' : 0,
				'LEFT' : 0,
				'RIGHT' : 0,
				'A' : 0,
				'B' : 0,
				'C' : 0,
				'D' : 0,
				'X' : 0,
				'Y' : 0,
				'Z' : 0,
				'LTRIG' : 0,
				'RTRIG' : 0,
				'START' : 0,
				'S1UP' : 0,
				'S1DOWN' : 0,
				'S1LEFT' : 0,
				'S1RIGHT' : 0,
				'S2UP' : 0,
				'S2DOWN' : 0,
				'S2LEFT' : 0,
				'S2RIGHT' : 0
			},
			'JOY0_1' : {
				'UP' : 0,
				'DOWN' : 0,
				'LEFT' : 0,
				'RIGHT' : 0,
				'A' : 0,
				'B' : 0,
				'C' : 0,
				'D' : 0,
				'X' : 0,
				'Y' : 0,
				'Z' : 0,
				'LTRIG' : 0,
				'RTRIG' : 0,
				'START' : 0,
				'S1UP' : 0,
				'S1DOWN' : 0,
				'S1LEFT' : 0,
				'S1RIGHT' : 0,
				'S2UP' : 0,
				'S2DOWN' : 0,
				'S2LEFT' : 0,
				'S2RIGHT' : 0
			},
			'JOY0_2' : {
				'UP' : 0,
				'DOWN' : 0,
				'LEFT' : 0,
				'RIGHT' : 0,
				'A' : 0,
				'B' : 0,
				'C' : 0,
				'D' : 0,
				'X' : 0,
				'Y' : 0,
				'Z' : 0,
				'LTRIG' : 0,
				'RTRIG' : 0,
				'START' : 0,
				'S1UP' : 0,
				'S1DOWN' : 0,
				'S1LEFT' : 0,
				'S1RIGHT' : 0,
				'S2UP' : 0,
				'S2DOWN' : 0,
				'S2LEFT' : 0,
				'S2RIGHT' : 0
			},
			'JOY0_3' : {
				'UP' : 0,
				'DOWN' : 0,
				'LEFT' : 0,
				'RIGHT' : 0,
				'A' : 0,
				'B' : 0,
				'C' : 0,
				'D' : 0,
				'X' : 0,
				'Y' : 0,
				'Z' : 0,
				'LTRIG' : 0,
				'RTRIG' : 0,
				'START' : 0,
				'S1UP' : 0,
				'S1DOWN' : 0,
				'S1LEFT' : 0,
				'S1RIGHT' : 0,
				'S2UP' : 0,
				'S2DOWN' : 0,
				'S2LEFT' : 0,
				'S2RIGHT' : 0
			},
			'JAMMA0_0' : {
				'PUSH1' : 0,
				'PUSH2' : 0,
				'PUSH3' : 0,
				'PUSH4' : 0,
				'PUSH5' : 0,
				'PUSH6' : 0,
				'PUSH7' : 0,
				'PUSH8' : 0,
				'SERVICE' : 0,
				'START' : 0,
				'COIN' : 0,
				'DIGITALUP' : 0,
				'DIGITALDOWN' : 0,
				'DIGITALLEFT' : 0,
				'DIGITALRIGHT' : 0,
				'ANALOGUP' : 0,
				'ANALOGDOWN' : 0,
				'ANALOGLEFT' : 0,
				'ANALOGRIGHT' : 0,
				'ANALOGUP2' : 0,
				'ANALOGDOWN2' : 0,
				'ANALOGLEFT2' : 0,
				'ANALOGRIGHT2' : 0
			},
			'JAMMA0_1' : {
				'PUSH1' : 0,
				'PUSH2' : 0,
				'PUSH3' : 0,
				'PUSH4' : 0,
				'PUSH5' : 0,
				'PUSH6' : 0,
				'PUSH7' : 0,
				'PUSH8' : 0,
				'SERVICE' : 0,
				'START' : 0,
				'COIN' : 0,
				'DIGITALUP' : 0,
				'DIGITALDOWN' : 0,
				'DIGITALLEFT' : 0,
				'DIGITALRIGHT' : 0,
				'ANALOGUP' : 0,
				'ANALOGDOWN' : 0,
				'ANALOGLEFT' : 0,
				'ANALOGRIGHT' : 0,
				'ANALOGUP2' : 0,
				'ANALOGDOWN2' : 0,
				'ANALOGLEFT2' : 0,
				'ANALOGRIGHT2' : 0
			},
			'JAMMA0_2' : {
				'PUSH1' : 0,
				'PUSH2' : 0,
				'PUSH3' : 0,
				'PUSH4' : 0,
				'PUSH5' : 0,
				'PUSH6' : 0,
				'PUSH7' : 0,
				'PUSH8' : 0,
				'SERVICE' : 0,
				'START' : 0,
				'COIN' : 0,
				'DIGITALUP' : 0,
				'DIGITALDOWN' : 0,
				'DIGITALLEFT' : 0,
				'DIGITALRIGHT' : 0,
				'ANALOGUP' : 0,
				'ANALOGDOWN' : 0,
				'ANALOGLEFT' : 0,
				'ANALOGRIGHT' : 0,
				'ANALOGUP2' : 0,
				'ANALOGDOWN2' : 0,
				'ANALOGLEFT2' : 0,
				'ANALOGRIGHT2' : 0
			},
			'JAMMA0_3' : {
				'PUSH1' : 0,
				'PUSH2' : 0,
				'PUSH3' : 0,
				'PUSH4' : 0,
				'PUSH5' : 0,
				'PUSH6' : 0,
				'PUSH7' : 0,
				'PUSH8' : 0,
				'SERVICE' : 0,
				'START' : 0,
				'COIN' : 0,
				'DIGITALUP' : 0,
				'DIGITALDOWN' : 0,
				'DIGITALLEFT' : 0,
				'DIGITALRIGHT' : 0,
				'ANALOGUP' : 0,
				'ANALOGDOWN' : 0,
				'ANALOGLEFT' : 0,
				'ANALOGRIGHT' : 0,
				'ANALOGUP2' : 0,
				'ANALOGDOWN2' : 0,
				'ANALOGLEFT2' : 0,
				'ANALOGRIGHT2' : 0
			},
			'MAHJONG0_0' : {
				'A' : 0,
				'B' : 0,
				'C' : 0,
				'D' : 0,
				'E' : 0,
				'F' : 0,
				'G' : 0,
				'H' : 0,
				'I' : 0,
				'J' : 0,
				'K' : 0,
				'L' : 0,
				'M' : 0,
				'N' : 0,
				'FF' : 0,
				'STR' : 0,
				'BET' : 0,
				'LST' : 0,
				'KAN' : 0,
				'PON' : 0,
				'CHI' : 0,
				'RCH' : 0,
				'RON' : 0
			},
			'GLOBAL0' : {
				'TEST' : 0,
				'TEST2' : 0,
				'SERVICE' : 0,
				'SAVESTATE' : 0,
				'LOADSTATE' : 0,
				'NEXTSTATE' : 0,
				'PREVSTATE' : 0,
				'DEADZONE' : 0
			},
			'JOY1_0' : {
				'UP' : 0,
				'DOWN' : 0,
				'LEFT' : 0,
				'RIGHT' : 0,
				'A' : 0,
				'B' : 0,
				'C' : 0,
				'D' : 0,
				'X' : 0,
				'Y' : 0,
				'Z' : 0,
				'LTRIG' : 0,
				'RTRIG' : 0,
				'START' : 0,
				'S1UP' : 0,
				'S1DOWN' : 0,
				'S1LEFT' : 0,
				'S1RIGHT' : 0,
				'S2UP' : 0,
				'S2DOWN' : 0,
				'S2LEFT' : 0,
				'S2RIGHT' : 0
			},
			'JOY1_1' : {
				'UP' : 0,
				'DOWN' : 0,
				'LEFT' : 0,
				'RIGHT' : 0,
				'A' : 0,
				'B' : 0,
				'C' : 0,
				'D' : 0,
				'X' : 0,
				'Y' : 0,
				'Z' : 0,
				'LTRIG' : 0,
				'RTRIG' : 0,
				'START' : 0,
				'S1UP' : 0,
				'S1DOWN' : 0,
				'S1LEFT' : 0,
				'S1RIGHT' : 0,
				'S2UP' : 0,
				'S2DOWN' : 0,
				'S2LEFT' : 0,
				'S2RIGHT' : 0
			},
			'JOY1_2' : {
				'UP' : 0,
				'DOWN' : 0,
				'LEFT' : 0,
				'RIGHT' : 0,
				'A' : 0,
				'B' : 0,
				'C' : 0,
				'D' : 0,
				'X' : 0,
				'Y' : 0,
				'Z' : 0,
				'LTRIG' : 0,
				'RTRIG' : 0,
				'START' : 0,
				'S1UP' : 0,
				'S1DOWN' : 0,
				'S1LEFT' : 0,
				'S1RIGHT' : 0,
				'S2UP' : 0,
				'S2DOWN' : 0,
				'S2LEFT' : 0,
				'S2RIGHT' : 0
			},
			'JOY1_3' : {
				'UP' : 0,
				'DOWN' : 0,
				'LEFT' : 0,
				'RIGHT' : 0,
				'A' : 0,
				'B' : 0,
				'C' : 0,
				'D' : 0,
				'X' : 0,
				'Y' : 0,
				'Z' : 0,
				'LTRIG' : 0,
				'RTRIG' : 0,
				'START' : 0,
				'S1UP' : 0,
				'S1DOWN' : 0,
				'S1LEFT' : 0,
				'S1RIGHT' : 0,
				'S2UP' : 0,
				'S2DOWN' : 0,
				'S2LEFT' : 0,
				'S2RIGHT' : 0
			},
			'JAMMA1_0' : {
				'PUSH1' : 0,
				'PUSH2' : 0,
				'PUSH3' : 0,
				'PUSH4' : 0,
				'PUSH5' : 0,
				'PUSH6' : 0,
				'PUSH7' : 0,
				'PUSH8' : 0,
				'SERVICE' : 0,
				'START' : 0,
				'COIN' : 0,
				'DIGITALUP' : 0,
				'DIGITALDOWN' : 0,
				'DIGITALLEFT' : 0,
				'DIGITALRIGHT' : 0,
				'ANALOGUP' : 0,
				'ANALOGDOWN' : 0,
				'ANALOGLEFT' : 0,
				'ANALOGRIGHT' : 0,
				'ANALOGUP2' : 0,
				'ANALOGDOWN2' : 0,
				'ANALOGLEFT2' : 0,
				'ANALOGRIGHT2' : 0
			},
			'JAMMA1_1' : {
				'PUSH1' : 0,
				'PUSH2' : 0,
				'PUSH3' : 0,
				'PUSH4' : 0,
				'PUSH5' : 0,
				'PUSH6' : 0,
				'PUSH7' : 0,
				'PUSH8' : 0,
				'SERVICE' : 0,
				'START' : 0,
				'COIN' : 0,
				'DIGITALUP' : 0,
				'DIGITALDOWN' : 0,
				'DIGITALLEFT' : 0,
				'DIGITALRIGHT' : 0,
				'ANALOGUP' : 0,
				'ANALOGDOWN' : 0,
				'ANALOGLEFT' : 0,
				'ANALOGRIGHT' : 0,
				'ANALOGUP2' : 0,
				'ANALOGDOWN2' : 0,
				'ANALOGLEFT2' : 0,
				'ANALOGRIGHT2' : 0
			},
			'JAMMA1_2' : {
				'PUSH1' : 0,
				'PUSH2' : 0,
				'PUSH3' : 0,
				'PUSH4' : 0,
				'PUSH5' : 0,
				'PUSH6' : 0,
				'PUSH7' : 0,
				'PUSH8' : 0,
				'SERVICE' : 0,
				'START' : 0,
				'COIN' : 0,
				'DIGITALUP' : 0,
				'DIGITALDOWN' : 0,
				'DIGITALLEFT' : 0,
				'DIGITALRIGHT' : 0,
				'ANALOGUP' : 0,
				'ANALOGDOWN' : 0,
				'ANALOGLEFT' : 0,
				'ANALOGRIGHT' : 0,
				'ANALOGUP2' : 0,
				'ANALOGDOWN2' : 0,
				'ANALOGLEFT2' : 0,
				'ANALOGRIGHT2' : 0
			},
			'JAMMA1_3' : {
				'PUSH1' : 0,
				'PUSH2' : 0,
				'PUSH3' : 0,
				'PUSH4' : 0,
				'PUSH5' : 0,
				'PUSH6' : 0,
				'PUSH7' : 0,
				'PUSH8' : 0,
				'SERVICE' : 0,
				'START' : 0,
				'COIN' : 0,
				'DIGITALUP' : 0,
				'DIGITALDOWN' : 0,
				'DIGITALLEFT' : 0,
				'DIGITALRIGHT' : 0,
				'ANALOGUP' : 0,
				'ANALOGDOWN' : 0,
				'ANALOGLEFT' : 0,
				'ANALOGRIGHT' : 0,
				'ANALOGUP2' : 0,
				'ANALOGDOWN2' : 0,
				'ANALOGLEFT2' : 0,
				'ANALOGRIGHT2' : 0
			},
			'MAHJONG01_0' : {
				'A' : 0,
				'B' : 0,
				'C' : 0,
				'D' : 0,
				'E' : 0,
				'F' : 0,
				'G' : 0,
				'H' : 0,
				'I' : 0,
				'J' : 0,
				'K' : 0,
				'L' : 0,
				'M' : 0,
				'N' : 0,
				'FF' : 0,
				'STR' : 0,
				'BET' : 0,
				'LST' : 0,
				'KAN' : 0,
				'PON' : 0,
				'CHI' : 0,
				'RCH' : 0,
				'RON' : 0
			},
			'GLOBAL1' : {
				'TEST' : 0,
				'TEST2' : 0,
				'SERVICE' : 0,
				'SAVESTATE' : 0,
				'LOADSTATE' : 0,
				'NEXTSTATE' : 0,
				'PREVSTATE' : 0,
				'DEADZONE' : 0
			}
		}

		// Setup the gamepad
		config['JOY0_0'] = {
			'UP' : BUTTON_CODE_MAP[self.button_map['btn_up_demul']],
			'DOWN' : BUTTON_CODE_MAP[self.button_map['btn_down_demul']],
			'LEFT' : BUTTON_CODE_MAP[self.button_map['btn_left_demul']],
			'RIGHT' : BUTTON_CODE_MAP[self.button_map['btn_right_demul']],
			'A' : BUTTON_CODE_MAP[self.button_map['btn_a_demul']],
			'B' : BUTTON_CODE_MAP[self.button_map['btn_b_demul']],
			'C' : 0,
			'D' : 0,
			'X' : BUTTON_CODE_MAP[self.button_map['btn_x_demul']],
			'Y' : BUTTON_CODE_MAP[self.button_map['btn_y_demul']],
			'Z' : 0,
			'LTRIG' : BUTTON_CODE_MAP[self.button_map['btn_l_trigger_demul']],
			'RTRIG' : BUTTON_CODE_MAP[self.button_map['btn_r_trigger_demul']],
			'START' : BUTTON_CODE_MAP[self.button_map['btn_start_demul']],
			'S1UP' : BUTTON_CODE_MAP[self.button_map['btn_left_stick_up_demul']],
			'S1DOWN' : BUTTON_CODE_MAP[self.button_map['btn_left_stick_down_demul']],
			'S1LEFT' : BUTTON_CODE_MAP[self.button_map['btn_left_stick_left_demul']],
			'S1RIGHT' : BUTTON_CODE_MAP[self.button_map['btn_left_stick_right_demul']],
			'S2UP' : BUTTON_CODE_MAP[self.button_map['btn_right_stick_up_demul']],
			'S2DOWN' : BUTTON_CODE_MAP[self.button_map['btn_right_stick_down_demul']],
			'S2LEFT' : BUTTON_CODE_MAP[self.button_map['btn_right_stick_left_demul']],
			'S2RIGHT' : BUTTON_CODE_MAP[self.button_map['btn_right_stick_right_demul']]
		}

		ini.write_ini_file('emulators/Demul/padDemul.ini', config)

	def _setup_spu(self):
		config = {
			'main' : {
				'spuDisable' : 'false',
				'cddaDisable' : 'false',
				'dspDisable' : 'false',
				'spuRecord' : 'false',
				'bufSize' : 2048
			}
		}
		ini.write_ini_file('emulators/Demul/spuDemul.ini', config)

	def _setup_net(self):
		config = {
			'main' : {
				'netEnable' : 'false',
				'swapDisable' : 'false',
				'NameOverride' : ''
			}
		}
		ini.write_ini_file('emulators/Demul/netDemul.ini', config)

	def _setup_gdr(self):
		config = {
			'main' : {
				'imageFileName' : '',
				'openDialog' : 'true'
			}
		}
		ini.write_ini_file('emulators/Demul/gdrImage.ini', config)

	def _setup_directx(self):
		global directx_version

		// Setup DirectX
		config = {
			'main' : {
				'Vsync' : 0,
				'AutoSort' : 0,
				'NetworkSort' : 0,
				'OModifier' : 0,
				'TModifier' : 0,
				'UseFullscreen' : 0,
				'rotate' : 0,
				'aspect' : 1,
				'scaling' : 1,
				'MaxLayers' : 32,
				'NotAutoRotate' : 0
			},
			'resolution' : {
				'Width' : 640,
				'Height' : 480
			},
			'shaders' : {
				'usePass1' : 0,
				'usePass2' : 0,
				'shaderPass1' : '',
				'shaderPass2' : ''
			}
		}

		if '11' in directx_version:
			ini.write_ini_file('emulators/Demul/gpuDX11.ini', config)
		elif '10' in directx_version:
			ini.write_ini_file('emulators/Demul/gpuDX10.ini', config)

	def _setup_demul(self):
		// Setup Demul
		config = {
			'files' : {
				'nvram' : os.path.abspath('emulators/Demul/nvram/'),
				'romsPathsCount' : 1,
				'roms0' : os.path.abspath('emulators/Demul/roms/')
			},
			'PORTD' : {
				'device' : -1,
				'port4' : -1,
				'port2' : -1,
				'port3' : -1,
				'port0' : -1,
				'port1' : -1
			},
			'PORTB' : {
				'device' : -1,
				'port4' : -1,
				'port2' : -1,
				'port3' : -1,
				'port0' : -1,
				'port1' : -1
			},
			'PORTC' : {
				'device' : -1,
				'port4' : -1,
				'port2' : -1,
				'port3' : -1,
				'port0' : -1,
				'port1' : -1
			},
			'PORTA' : {
				'device' : 16777216,
				'port4' : -1,
				'port2' : -1,
				'port3' : -1,
				'port0' : 234881024,
				'port1' : 65536
			},
			'plugins' : {
				'gdr' : 'gdrImage.dll',
				'spu' : 'spuDemul.dll',
				'pad' : 'padDemul.dll',
				'directory' : os.path.abspath('emulators/Demul/plugins/'),
				'gpu' : gpu_dll_version,
				'net' : 'netDemul.dll'
			},
			'main' : {
				'windowY' : 100,
				'windowX' : 100,
				'VMUscreendisable' : 'false',
				'dcBios' : 3,
				'region' : 1,
				'activateBBA' : 'false',
				'cpumode' : 1,
				'hikaruBios' : 1,
				'naomiBiosAuto' : 'true',
				'broadcast' : 1,
				'lastEmuRunMode' : 0,
				'naomifreq' : 1,
				'naomiLLEMIE' : 'false',
				'timehack' : 'true',
				'videomode' : 768
			},
			'VMS' : {
				'VMSA4' : '',
				'VMSA0' : os.path.abspath('emulators/Demul/memsaves/vms00.bin'),
				'VMSA1' : '',
				'VMSA2' : '',
				'VMSA3' : '',
				'VMSC2' : '',
				'VMSD4' : '',
				'VMSD0' : '',
				'VMSD2' : '',
				'VMSD1' : '',
				'VMSC3' : '',
				'VMSD3' : '',
				'VMSC0' : '',
				'VMSB4' : '',
				'VMSC4' : '',
				'VMSC1' : '',
				'VMSB1' : '',
				'VMSB0' : '',
				'VMSB3' : '',
				'VMSB2' : ''
			}
		}
		ini.write_ini_file('emulators/Demul/Demul.ini', config)
		return config

	def run(self, path, binary, on_stop=None):
		// Setup ini files
		self._setup_spu()
		self._setup_pad()
		self._setup_net()
		self._setup_gdr()
		self._setup_directx()
		config = self._setup_demul()

		// Get the window title
		directx_dll = config['plugins']['gpu']
		window_name = None
		if not path and not binary:
			window_name = 'Demul'
		elif directx_dll == 'gpuDX11.dll':
			window_name = 'gpuDX11'
		elif directx_dll == 'gpuDX10.dll':
			window_name = 'gpuDX10'

		os.chdir("emulators/Demul/")

		// Figure out if running a game or not
		command = None
		full_screen = False
		if binary:
			command = '"demul.exe" -run=dc -image="' + binary + '"'
			full_screen = True
		else:
			command = '"demul.exe" -run=dc'
			full_screen = False

		// Run the game
		runner = emu_runner.EmuRunner(command, window_name, full_screen, full_screen_alt_enter=True)
		runner.run()
		os.chdir("../..")

		// Upload the memory card to the server
		if on_stop:
			with open("emulators/Demul/memsaves/vms00.bin", 'rb') as f:
				memory_card = f.read()
			on_stop(memory_card)
*/
