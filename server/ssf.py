#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2015, Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# emu_archive is a HTML based front end for video game console emulators
# It uses a MIT style license
# It is hosted at: https://github.com/workhorsy/emu_archive
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os, sys

import ini
import emu_runner
import base_console
import file_mounter


class SSF(base_console.BaseConsole):
	def __init__(self):
		super(SSF, self).__init__('config/ssf.json')

	def _setup_configs(self, bios_path):
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
				'Pad0_0_0' : '"2/200/2/208/2/203/2/205/2/44/2/45/2/46/2/31/2/32/2/33/2/30/2/34/2/28/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0"',
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

		# Save SSF.ini
		ini.write_ini_file('emulators/SSF_012_beta_R4/SSF.ini', config)
		
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
		ini.write_ini_file('emulators/SSF_012_beta_R4/SSF.ini', config)

	def run(self, path, binary, bios):
		# Mount the game
		mounter = file_mounter.FileMounter("D")
		mounter.unmount()
		mounter.mount(path + '/' + binary)

		# Get the bios path
		bios_path = bios
		if bios_path:
			bios_path = os.path.abspath('emulators/SSF_012_beta_R4/bios/' + bios_path)

		self._setup_configs(bios_path)

		# Run the game
		os.chdir("emulators/SSF_012_beta_R4/")
		game_path = self.goodJoin("../../", path + '/' + binary)
		command = '"SSF.exe" "' + game_path + '"'
		runner = emu_runner.EmuRunner(command, 'SSF', full_screen_alt_enter=True)
		runner.run()
		os.chdir("../..")

