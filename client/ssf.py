#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2015, Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# emulators-online is a HTML based front end for video game console emulators
# It uses the GNU AGPL 3 license
# It is hosted at: https://github.com/workhorsylegacy/emulators-online
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, sys

import ini
import emu_runner
import base_console
import file_mounter

BUTTON_CODE_MAP = {
	'button_12' : '1/34822/', # up
	'button_13' : '1/34823/', # down
	'button_14' : '1/34824/', # left
	'button_15' : '1/34825/', # right
	'button_0' : '1/0/', # a
	'button_1' : '1/256/', # b
	'button_2' : '1/512/', # x
	'button_3' : '1/768/', # y
	'button_4' : '1/1024/', # L Shoulder
	'button_5' : '1/1280/', # R Shoulder
	'button_7' : '1/33282/', # L Trigger
	'button_6' : '1/33281/', # R Trigger
	'button_9' : '1/1792/', # Start
	'axes_1-' : '1/33025/', # L Stick Up
	'axes_1+' : '1/33026/', # L Stick Down
	'axes_0-' : '1/32769/', # L Stick Left
	'axes_0+' : '1/32770/', # L Stick Right
	'axes_3-' : '1/33793/', # R Stick Up
	'axes_3+' : '1/33794/', # R Stick Down
	'axes_2-' : '1/33537/', # R Stick Left
	'axes_2+' : '1/33538/', # R Stick Right
}

KEYBOARD_IBM_CODE_MAP = {
	'none' : 0,
	'ESCAPE' : 1,
	'1' : 2,
	'2' : 3,
	'3' : 4,
	'4' : 5,
	'5' : 6,
	'6' : 7,
	'7' : 8,
	'8' : 9,
	'9' : 10,
	'0' : 11,
	'MINUS' : 12,
	'EQUALS' : 13,
	'BACKSPACE' : 14,
	'TAB' : 15,
	'Q' : 16,
	'W' : 17,
	'E' : 18,
	'R' : 19,
	'T' : 20,
	'Y' : 21,
	'U' : 22,
	'I' : 23,
	'O' : 24,
	'P' : 25,
	'LBRACKET' : 26,
	'RBRACKET' : 27,
	'RETURN' : 28,
	'LCONTROL' : 29,
	'A' : 30,
	'S' : 31,
	'D' : 32,
	'F' : 33,
	'G' : 34,
	'H' : 35,
	'J' : 36,
	'K' : 37,
	'L' : 38,
	'SEMICOLON': 39,
	'APOSTROPHE' : 40, # '
	'GRAVE' : 41, # `
	'LSHIFT' : 42,
	'BACKSLASH' : 43,
	'Z' : 44,
	'X' : 45,
	'C' : 46,
	'V' : 47,
	'B' : 48,
	'N' : 49,
	'M' : 50,
	'COMMA' : 51,
	'PERIOD' : 52,
	'SLASH' : 53,
	'RSHIFT' : 54,
	'MULTIPLY' : 55, # ×
	'LMENU' : 56, # Left Menu/Alt
	'SPACE' : 57,
	'CAPITAL' : 58, # Caps Lock
	'F1' : 59,
	'F2' : 60,
	'F3' : 61,
	'F4' : 62,
	'F5' : 63,
	'F6' : 64,
	'F7' : 65,
	'F8' : 66,
	'F9' : 67,
	'F10' : 68,
	'NUMLOCK' : 69,
	'SCROLL' : 70,	
	'NUMPAD7' : 71,
	'NUMPAD8' : 72,
	'NUMPAD9' : 73,
	'SUBTRACT' : 74,
	'NUMPAD4' : 75,
	'NUMPAD5' : 76,
	'NUMPAD6' : 77,
	'ADD' : 78,
	'NUMPAD1' : 79,
	'NUMPAD2' : 80,
	'NUMPAD3' : 81,
	'NUMPAD0' : 82,
	'DECIMAL' : 83,
	'F11' : 87,
	'F12' : 88,
	'F13' : 100,
	'F14' : 101,
	'F15' : 102,
	'F16' : 103,
	'F17' : 104,
	'F18' : 105,
	'KANA' : 112,
	'F19' : 113,
	'CONVERT' : 121,
	'NOCONVERT' : 123,
	'YEN' : 125, # ¥
	'NUMPADEQUALS' : 141,
	'CIRCUMFLEX' : 144, # ^
	'AT' : 145, # @
	'COLON' : 146, # :
	'UNDERLINE' : 147, # _
	'KANJI' : 148,
	'STOP' : 149,
	'AX' : 150,
	'UNLABLED' : 151,
	'NUMPADENTER' : 156,
	'RCONTROL' : 157,
	'SECTION' : 157,
	'NUMPADCOMMA' : 179,
	'DIVIDE' : 181,
	'SYSRQ' : 183,
	'RMENU' : 184, # Right Menu/Alt
	'FUNCTION' : 196,
	'PAUSE' : 197, 
	'HOME' : 199,
	'UP' : 200,
	'PRIOR': 201, # Page Up
	'LEFT' : 203, # Left Arrow
	'RIGHT' : 205, # Right Arrow
	'END' : 207,
	'DOWN' : 208, # Down Arrow
	'NEXT' : 209, # Page Down
	'INSERT' : 210,
	'DELETE' : 211,
	'LMETA' : 219, # Left Meta/Super
	'LWIN' : 219,
	'RMETA' : 220, # Right Meta/Super
	'RWIN' : 220,
	'APPS' : 221,
	'POWER' : 222,
	'SLEEP' : 223
}


class SSF(base_console.BaseConsole):
	def __init__(self):
		super(SSF, self).__init__('config/ssf.json')

		# Setup the initial map, if there is none
		if not self.button_map:
			self.button_map = {
				'btn_up_ssf' : None,
				'btn_down_ssf' : None,
				'btn_left_ssf' : None,
				'btn_right_ssf' : None,
				'btn_start_ssf' : None,
				'btn_a_ssf' : None,
				'btn_b_ssf' : None,
				'btn_c_ssf' : None,
				'btn_x_ssf' : None,
				'btn_y_ssf' : None,
				'btn_z_ssf' : None,
				'btn_l_shoulder_ssf' : None,
				'btn_r_shoulder_ssf' : None,
			}

	def is_installed(self):
		return os.path.isdir('emulators/SSF_012_beta_R4/')

	def _setup_configs(self, bios_path):
		# Figure out the BIOS
		if not bios_path:
			bios_path = ''

		config = {
			'Peripheral' : {
				'SaturnBIOS' : '"' + bios_path + '"', # use the regions bios
				'STVBIOS' : '""',
				'CDDrive' : '"0"',
				'CartridgeID' : '"5c"',
				'Areacode' : '"1"',
				'DataCartridgeEnable' : '"0"',
				'DataCartridge' : '""'
			},
			'Screen' : {
				'Scanline' : '"0"',
				'ScanlineRatio' : '"70"',
				'DisableFullscreenScanline' : '"1"',
				'AutoFieldSkip' : '"1"',
				'EnforceAspectRatioWindow' : '"1"',
				'EnforceAspectRatioFullscreen' : '"1"',
				'WideScreen' : '"0"',
				'VSynchWaitWindow' : '"0"',
				'VSynchWaitFullscreen' : '"0"',
				'FixedWindowResolution' : '"0"',
				'FixedFullscreenResolution' : '"0"',
				'BilinearFiltering' : '"0"',
				'StretchScreen' : '"1"',
				'FullSize' : '"1"',
				'FullscreenDisplay' : '"0"',
			},
			'Sound' : {
				'LinearFiltering' : '"1"',
				'DoublePrecision' : '"0"',
				'Mute' : '"0"',
				'Volume' : '"1.00"',
				'VolumeAdd' : '"0.25"',
				'BufferSize' : '"2"'
			},
			'Program1' : {
				'DisableInput' : '"1"',
				'FlipThread' : '"0"',
				'VDP1DrawThread' : '"0"',
				'VDP1ThreadNumber' : '"1"',
				'VDP1ThreadAlwaysRunning' : '"0"',
				'VDP1Division' : '"1"',
				'VDP2DrawThread' : '"1"',
				'VDP2ThreadNumber' : "11",
				'SoundThread' : '"1"',
				'CDBlockThread' : '"0"',
				'CDBlockNoWait' : '"0"',
				'ScanlineBaseTiming' : '"0"',
				'DSPThread' : '"0"',
				'DSPThreadAlwaysRunning' : '"0"',
				'DSPDynamicRecompile' : '"1"',
				'Priority' : '"2"'
			},
			'Program2' : {
				'CDDriveReadSectors' : '"8"',
				'DotClock' : '"2.50"',
				'BlockClock' : '"80"',
				'CheckSlaveSH2IdleLoop' : '"1"',
				'SlaveSH2Speed' : '"90"',
				'SH2RecompileBlockInstructions' : '"40"',
				'CDSectorNumbersPerSecond' : '"150"',
				'SH2RecompileBufferSize' : '"8"',
				'SH2RecompileBlockNumber' : '"40000"',
				'AlternativeSH2Recompile' : '"0"',
				'CheckMemoryAccess' : '"0"',
			},
			'Program3' : {
				'CheckSpritePriority' : '"0"',
				'CheckCyclePattern' : '"1"',
				'VDP2RAMRevisionAccess' : '"1"',
				'VDP2RAMWriteTiming' : '"0"',
				'VDP2RAMWriteTimingBufferSize' : '"24"',
				'MemoryAccessWait' : '"0"',
				'SH2Cache' : '"0"',
				'EnableInstructionCache' : '"0"',
				'BusWait' : '"0"',
				'BusWaitClock' : '"1"',
				'SH2DMARealTransfer' : '"0"',
				'SCUDMADelayInterrupt' : '"0"',
				'CDTrackIndex' : '"0"',
				'BranchInstructionClock' : '"0"',
			},
			'Program4' : {
				'CDAccessLED' : '"1"',
				'NoBIOS' : '"0"',
				'HookBackupLibrary' : '"1"',
				'EnableFDD' : '"0"',
				'MeshTranslucent' : '"0"',
				'Deinterlace' : '"0"',
				'EmulateSpeedAdd' : '"0.50"',
				'68000Type' : '"0"',
				'ShowRegister' : '"0"',
				'EnableCDImage' : '"0"',
				'CDImage' : '""'
			},
			'SSFV' : {
				'FrameRate' : '"30"',
				'KeyFrameInterval' : '"60"',
				'QuantumLevel' : '"1"',
				'HalfSize' : '"1"',
				'Thread' : '"1"',
			},
			'SpeedTest' : {
				'Enable' : '"0"',
				'Draw' : '"1"',
				'CDBlockNoWait' : '"1"',
				'Time' : '"300"',
				'SingleCPU' : '"0"',
			},
			'Input' : {
				'PortFlag0' : '"0"',
				'PortFlag1' : '"0"',
				'PadType0_0' : '"0"',
				'PadType0_1' : '"5"',
				'PadType0_2' : '"5"',
				'PadType0_3' : '"5"',
				'PadType0_4' : '"5"',
				'PadType0_5' : '"5"',
				'PadType1_0' : '"5"',
				'PadType1_1' : '"5"',
				'PadType1_2' : '"5"',
				'PadType1_3' : '"5"',
				'PadType1_4' : '"5"',
				'PadType1_5' : '"5"',
				'Pad0_0_0' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_0_1' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_0_2' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_0_3' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_1_0' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_1_1' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_1_2' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_1_3' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_2_0' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_2_1' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_2_2' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_2_3' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_3_0' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_3_1' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_3_2' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_3_3' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_4_0' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_4_1' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_4_2' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_4_3' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_5_0' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_5_1' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_5_2' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad0_5_3' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_0_0' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_0_1' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_0_2' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_0_3' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_1_0' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_1_1' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_1_2' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_1_3' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_2_0' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_2_1' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_2_2' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_2_3' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_3_0' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_3_1' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_3_2' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_3_3' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_4_0' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_4_1' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_4_2' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_4_3' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_5_0' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_5_1' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_5_2' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Pad1_5_3' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Rapid0_0' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Rapid0_1' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Rapid0_2' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Rapid0_3' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Rapid0_4' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Rapid0_5' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Rapid1_0' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Rapid1_1' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Rapid1_2' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Rapid1_3' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Rapid1_4' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'Rapid1_5' : '"0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
				'VariableRapid0_0' : '"0"',
				'VariableRapid0_1' : '"0"',
				'VariableRapid0_2' : '"0"',
				'VariableRapid0_3' : '"0"',
				'VariableRapid0_4' : '"0"',
				'VariableRapid0_5' : '"0"',
				'VariableRapid1_0' : '"0"',
				'VariableRapid1_1' : '"0"',
				'VariableRapid1_2' : '"0"',
				'VariableRapid1_3' : '"0"',
				'VariableRapid1_4' : '"0"',
				'VariableRapid1_5' : '"0"',
				'EnableRapid' : '"0"',
			},
			'Other' : {
				'SMEM0' : '"0"',
				'SMEM1' : '"0"',
				'SMEM2' : '"0"',
				'SMEM3' : '"5"',
				'DateFlag' : '"1"',
				'SSDate0' : '"2015"',
				'SSDate1' : '"1"',
				'SSDate2' : '"6"',
				'SSDate3' : '"31"',
				'SSDate4' : '"16"',
				'SSDate5' : '"59"',
				'SSDate6' : '"16"',
				'SSDate7' : '"12"',
				'ScreenMode' : '"0"', # Full screen
				'WindowSize' : '"0"',
				'WindowX' : '"830"',
				'WindowY' : '"255"',
				'ROMFolder' : '".\"'
			}
		}

		# Gamepad
		config['Input']['Pad0_0_0'] = \
			'"' + \
			BUTTON_CODE_MAP[self.button_map['btn_up_ssf']] + \
			BUTTON_CODE_MAP[self.button_map['btn_down_ssf']] + \
			BUTTON_CODE_MAP[self.button_map['btn_left_ssf']] + \
			BUTTON_CODE_MAP[self.button_map['btn_right_ssf']] + \
			BUTTON_CODE_MAP[self.button_map['btn_a_ssf']] + \
			BUTTON_CODE_MAP[self.button_map['btn_b_ssf']] + \
			BUTTON_CODE_MAP[self.button_map['btn_c_ssf']] + \
			BUTTON_CODE_MAP[self.button_map['btn_x_ssf']] + \
			BUTTON_CODE_MAP[self.button_map['btn_y_ssf']] + \
			BUTTON_CODE_MAP[self.button_map['btn_z_ssf']] + \
			BUTTON_CODE_MAP[self.button_map['btn_l_shoulder_ssf']] + \
			BUTTON_CODE_MAP[self.button_map['btn_r_shoulder_ssf']] + \
			BUTTON_CODE_MAP[self.button_map['btn_start_ssf']] + \
			'0/0' + \
			'0/0' + \
			'0/0' + \
			'0/0' + \
			'0/0' + \
			'0/0' + \
			'0/0' + \
			'0/0' + \
			'0/0' + \
			'0/0' + \
			'0/0' + \
			'0/0' + \
			'0/0' + \
			'"'

		# Save SSF.ini
		ini.WriteIniFile('emulators/SSF_012_beta_R4/SSF.ini', config)
		
		config = {
			# CardridgeID
			#  00 = none
			#  21 = Backup RAM Cartridge
			#  5a = 1MBytes RAM Cartridge
			#  5c = 4MBytes RAM Cartridge
			#
			# Areacode
			#  1 = Japan
			#  2 = Taiwan, Korea, Philippines
			#  4 = America, Canada, Brazil
			#  c = Europe, Australia, South Africa

			# Standard Setting
			'Setting1' : {
				'CartridgeID' : '"5c"',
				'Areacode' : '"1"',
				'DataCartridgeEnable' : '"0"',
				'DataCartridge' : '""',
				'WideScreen' : '"0"',
				'Volume' : '"1.00"',
				'VDP1DrawThread' : '"0"',
				'VDP1ThreadNumber' : '"1"',
				'VDP1ThreadAlwaysRunning' : '"0"',
				'VDP1Division' : '"1"',
				'VDP2DrawThread' : '"1"',
				'VDP2ThreadNumber' : '"11"',
				'SoundThread' : '"1"',
				'CDBlockThread' : '"0"',
				'CDBlockNoWait' : '"0"',
				'ScanlineBaseTiming' : '"0"',
				'DSPThread' : '"0"',
				'DSPThreadAlwaysRunning' : '"0"',
				'DSPDynamicRecompile' : '"1"',
				'DotClock' : '"2.50"',
				'1BlockClock' : '"100"',
				'CheckSlaveSH2IdleLoop' : '"1"',
				'SlaveSH2Speed' : '"90"',
				'SH2RecompileBlockInstructions' : '"40"',
				'SH2RecompileBufferSize' : '"8"',
				'SH2RecompileBlockNumber' : '"40000"',
				'AlternativeSH2Recompile' : '"0"',
				'CheckSpritePriority' : '"0"',
				'CheckCyclePattern' : '"1"',
				'VDP2RAMRevisionAccess' : '"1"',
				'VDP2RAMWriteTiming' : '"0"',
				'VDP2RAMWriteTimingBufferSize' : '"24"',
				'MemoryAccessWait' : '"0"',
				'SH2Cache' : '"0"',
				'EnableInstructionCache' : '"0"',
				'BusWait' : '"0"',
				'BusWaitClock' : '"0"',
				'SH2DMARealTransfer' : '"0"',
				'SCUDMADelayInterrupt' : '"0"',
				'CDTrackIndex' : '"0"',
				'BranchInstructionClock' : '"0"',
				'MeshTranslucent' : '"0"',
				'Deinterlace' : '"0"'
			},
			# High Setting
			'Setting2' : {
				'CartridgeID' : '"5c"',
				'Areacode' : '"1"',
				'DataCartridgeEnable' : '"0"',
				'DataCartridge' : '""',
				'WideScreen' : '"0"',
				'Volume' : '"1.00"',
				'VDP1DrawThread' : '"0"',
				'VDP1ThreadNumber' : '"1"',
				'VDP1ThreadAlwaysRunning' : '"0"',
				'VDP1Division' : '"1"',
				'VDP2DrawThread' : '"1"',
				'VDP2ThreadNumber' : '"11"',
				'SoundThread' : '"1"',
				'CDBlockThread' : '"0"',
				'CDBlockNoWait' : '"0"',
				'ScanlineBaseTiming' : '"0"',
				'DSPThread' : '"0"',
				'DSPThreadAlwaysRunning' : '"0"',
				'DSPDynamicRecompile' : '"1"',
				'DotClock' : '"3.20"',
				'1BlockClock' : '"90"',
				'CheckSlaveSH2IdleLoop' : '"1"',
				'SlaveSH2Speed' : '"90"',
				'SH2RecompileBlockInstructions' : '"40"',
				'SH2RecompileBufferSize' : '"8"',
				'SH2RecompileBlockNumber' : '"40000"',
				'AlternativeSH2Recompile' : '"0"',
				'CheckSpritePriority' : '"0"',
				'CheckCyclePattern' : '"1"',
				'VDP2RAMRevisionAccess' : '"1"',
				'VDP2RAMWriteTiming' : '"0"',
				'VDP2RAMWriteTimingBufferSize' : '"24"',
				'MemoryAccessWait' : '"0"',
				'SH2Cache' : '"0"',
				'EnableInstructionCache' : '"0"',
				'BusWait' : '"0"',
				'BusWaitClock' : '"0"',
				'SH2DMARealTransfer' : '"0"',
				'SCUDMADelayInterrupt' : '"0"',
				'CDTrackIndex' : '"0"',
				'BranchInstructionClock' : '"0"',
				'MeshTranslucent' : '"0"',
				'Deinterlace' : '"0"'
			},
			# Higher Setting
			'Setting3' : {
				'CartridgeID' : '"5c"',
				'Areacode' : '"1"',
				'DataCartridgeEnable' : '"0"',
				'DataCartridge' : '""',
				'WideScreen' : '"0"',
				'Volume' : '"1.00"',
				'VDP1DrawThread' : '"0"',
				'VDP1ThreadNumber' : '"1"',
				'VDP1ThreadAlwaysRunning' : '"0"',
				'VDP1Division' : '"1"',
				'VDP2DrawThread' : '"1"',
				'VDP2ThreadNumber' : '"11"',
				'SoundThread' : '"1"',
				'CDBlockThread' : '"0"',
				'CDBlockNoWait' : '"0"',
				'ScanlineBaseTiming' : '"0"',
				'DSPThread' : '"0"',
				'DSPThreadAlwaysRunning' : '"0"',
				'DSPDynamicRecompile' : '"1"',
				'DotClock' : '"3.70"',
				'1BlockClock' : '"80"',
				'CheckSlaveSH2IdleLoop' : '"1"',
				'SlaveSH2Speed' : '"100"',
				'SH2RecompileBlockInstructions' : '"40"',
				'SH2RecompileBufferSize' : '"8"',
				'SH2RecompileBlockNumber' : '"40000"',
				'AlternativeSH2Recompile' : '"0"',
				'CheckSpritePriority' : '"0"',
				'CheckCyclePattern' : '"1"',
				'VDP2RAMRevisionAccess' : '"1"',
				'VDP2RAMWriteTiming' : '"0"',
				'VDP2RAMWriteTimingBufferSize' : '"24"',
				'MemoryAccessWait' : '"1"',
				'SH2Cache' : '"0"',
				'EnableInstructionCache' : '"0"',
				'BusWait' : '"0"',
				'BusWaitClock' : '"0"',
				'SH2DMARealTransfer' : '"0"',
				'SCUDMADelayInterrupt' : '"0"',
				'CDTrackIndex' : '"0"',
				'BranchInstructionClock' : '"0"',
				'MeshTranslucent' : '"0"',
				'Deinterlace' : '"0"',
			},
			# Highest Setting
			'Setting4' : {
				'CartridgeID' : '"5c"',
				'Areacode' : '"1"',
				'DataCartridgeEnable' : '"0"',
				'DataCartridge' : '""',
				'WideScreen' : '"0"',
				'Volume' : '"1.00"',
				'VDP1DrawThread' : '"0"',
				'VDP1ThreadNumber' : '"1"',
				'VDP1ThreadAlwaysRunning' : '"0"',
				'VDP1Division' : '"1"',
				'VDP2DrawThread' : '"1"',
				'VDP2ThreadNumber' : '"11"',
				'SoundThread' : '"1"',
				'CDBlockThread' : '"0"',
				'CDBlockNoWait' : '"0"',
				'ScanlineBaseTiming' : '"0"',
				'DSPThread' : '"0"',
				'DSPThreadAlwaysRunning' : '"0"',
				'DSPDynamicRecompile' : '"1"',
				'DotClock' : '"3.90"',
				'1BlockClock' : '"80"',
				'CheckSlaveSH2IdleLoop' : '"1"',
				'SlaveSH2Speed' : '"100"',
				'SH2RecompileBlockInstructions' : '"40"',
				'SH2RecompileBufferSize' : '"8"',
				'SH2RecompileBlockNumber' : '"40000"',
				'AlternativeSH2Recompile' : '"0"',
				'CheckSpritePriority' : '"0"',
				'CheckCyclePattern' : '"1"',
				'VDP2RAMRevisionAccess' : '"1"',
				'VDP2RAMWriteTiming' : '"0"',
				'VDP2RAMWriteTimingBufferSize' : '"24"',
				'MemoryAccessWait' : '"1"',
				'SH2Cache' : '"0"',
				'EnableInstructionCache' : '"0"',
				'BusWait' : '"0"',
				'BusWaitClock' : '"0"',
				'SH2DMARealTransfer' : '"0"',
				'SCUDMADelayInterrupt' : '"0"',
				'CDTrackIndex' : '"0"',
				'BranchInstructionClock' : '"0"',
				'MeshTranslucent' : '"0"',
				'Deinterlace' : '"0"',
			},
			# Full Setting
			'Setting5' : {
				'CartridgeID' : '"5c"',
				'Areacode' : '"1"',
				'DataCartridgeEnable' : '"0"',
				'DataCartridge' : '""',
				'WideScreen' : '"0"',
				'Volume' : '"1.00"',
				'VDP1DrawThread' : '"0"',
				'VDP1ThreadNumber' : '"1"',
				'VDP1ThreadAlwaysRunning' : '"0"',
				'VDP1Division' : '"1"',
				'VDP2DrawThread' : '"1"',
				'VDP2ThreadNumber' : '"11"',
				'SoundThread' : '"1"',
				'CDBlockThread' : '"0"',
				'CDBlockNoWait' : '"0"',
				'ScanlineBaseTiming' : '"0"',
				'DSPThread' : '"0"',
				'DSPThreadAlwaysRunning' : '"0"',
				'DSPDynamicRecompile' : '"1"',
				'DotClock' : '"4.00"',
				'1BlockClock' : '"32"',
				'CheckSlaveSH2IdleLoop' : '"1"',
				'SlaveSH2Speed' : '"100"',
				'SH2RecompileBlockInstructions' : '"40"',
				'SH2RecompileBufferSize' : '"8"',
				'SH2RecompileBlockNumber' : '"40000"',
				'AlternativeSH2Recompile' : '"0"',
				'CheckSpritePriority' : '"0"',
				'CheckCyclePattern' : '"1"',
				'VDP2RAMRevisionAccess' : '"1"',
				'VDP2RAMWriteTiming' : '"1"',
				'VDP2RAMWriteTimingBufferSize' : '"24"',
				'MemoryAccessWait' : '"0"',
				'SH2Cache' : '"0"',
				'EnableInstructionCache' : '"0"',
				'BusWait' : '"1"',
				'BusWaitClock' : '"0"',
				'SH2DMARealTransfer' : '"1"',
				'SCUDMADelayInterrupt' : '"1"',
				'CDTrackIndex' : '"0"',
				'BranchInstructionClock' : '"0"',
				'MeshTranslucent' : '"0"',
				'Deinterlace' : '"0"',
			}
		}

		# Save Setting.ini
		ini.WriteIniFile('emulators/SSF_012_beta_R4/Setting.ini', config)

	def run(self, path, binary, bios_path):
		# Unmount any games
		mounter = file_mounter.FileMounter("D") # FIXME: The virtual drive is hard coded to D
		mounter.unmount()

		# Mount the game if needed
		if path and binary:
			mounter.mount(path + '/' + binary)

		# Get the bios path
		if bios_path:
			bios_path = os.path.abspath('emulators/SSF_012_beta_R4/bios/' + bios_path)

		self._setup_configs(bios_path)

		os.chdir("emulators/SSF_012_beta_R4/")

		# Figure out if running a game or not
		command = None
		full_screen = False
		if path and binary and bios_path:
			game_path = self.goodJoin("../../", path + '/' + binary)
			command = '"SSF.exe" "' + game_path + '"'
			full_screen = True
		else:
			command = '"SSF.exe"'
			full_screen = False

		# Run the game
		runner = emu_runner.EmuRunner(command, 'SSF', full_screen, full_screen_alt_enter=True)
		runner.run()
		os.chdir("../..")

