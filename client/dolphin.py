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


BUTTON_CODE_MAP = {
	'button_12' : '`Pad N`', # up
	'button_13' : '`Pad S`', # down
	'button_14' : '`Pad W`', # left
	'button_15' : '`Pad E`', # right
	'button_9' : 'Start', # start
	'button_0' : '`Button A`', # A
	'button_1' : '`Button B`', # B
	'button_2' : '`Button X`', # X
	'button_3' : '`Button Y`', # Y
	'button_8' : 'Back', # Back
	'button_10' : '`Thumb L`', # L stick click
	'button_11' : '`Thumb R`', # R stick click
	'button_7' : '`Trigger L`', # L Trigger
	'button_6' : '`Trigger R`', # R Trigger
	'button_4' : '`Shoulder L`', # L Shoulder button
	'button_5' : '`Shoulder R`', # R Shoulder button
	'axes_0-' : '`Left X-`', # L Stick Left
	'axes_0+' : '`Left X+`', # L Stick Right
	'axes_1-' : '`Left Y+`', # L Stick Up
	'axes_1+' : '`Left Y-`', # L Stick Down
	'axes_2-' : '`Right X-`', # R Stick Left
	'axes_2+' : '`Right X+`', # R Stick Right
	'axes_3-' : '`Right Y+`', # R Stick Up
	'axes_3+' : '`Right Y-`', # R Stick Down
	None : ''
}


class Dolphin(base_console.BaseConsole):
	def __init__(self):
		super(Dolphin, self).__init__('config/dolphin.json')

		# Setup the initial map, if there is none
		if not self.button_map:
			self.button_map = {
				'btn_up_dolphin' : None,
				'btn_down_dolphin' : None,
				'btn_left_dolphin' : None,
				'btn_right_dolphin' : None,
				'btn_start_dolphin' : None,
				'btn_a_dolphin' : None,
				'btn_b_dolphin' : None,
				'btn_x_dolphin' : None,
				'btn_y_dolphin' : None,
				'btn_z_dolphin' : None,
				'btn_l_trigger_dolphin' : None,
				'btn_r_trigger_dolphin' : None,
				'btn_l_shoulder_dolphin' : None,
				'btn_r_shoulder_dolphin' : None,
				'btn_left_stick_click_dolphin' : None,
				'btn_right_stick_click_dolphin' : None,
				'btn_left_stick_up_dolphin' : None,
				'btn_left_stick_down_dolphin' : None,
				'btn_left_stick_left_dolphin' : None,
				'btn_left_stick_right_dolphin' : None,
				'btn_right_stick_up_dolphin' : None,
				'btn_right_stick_down_dolphin' : None,
				'btn_right_stick_left_dolphin' : None,
				'btn_right_stick_right_dolphin' : None
			}

	def is_installed(self):
		return os.path.exists('emulators/Dolphin-x64/')

	def _setup_configs(self):
		global BUTTON_CODE_MAP

		# Create the directories if needed
		if not os.path.isdir(os.path.expanduser('~/Documents/Dolphin Emulator/')):
			os.mkdir(os.path.expanduser('~/Documents/Dolphin Emulator/'))
		if not os.path.isdir(os.path.expanduser('~/Documents/Dolphin Emulator/Config/')):
			os.mkdir(os.path.expanduser('~/Documents/Dolphin Emulator/Config/'))

		# Create Dolphin.ini
		ini_dolphin = os.path.expanduser('~/Documents/Dolphin Emulator/Config/Dolphin.ini')
		config = {
			'General' : {
				'LastFilename' : '',
				'ShowLag' : False,
				'ShowFrameCount' : False,
				'ISOPaths' : 1,
				'RecursiveISOPaths' : True,
				'NANDRootPath' : os.path.expanduser('~/Documents/Dolphin Emulator/Wii'),
				'WirelessMac' : '00:17:ab:96:76:3d', # FIXME Get the real MAC Address here
				'ISOPath0' : os.path.abspath('/emulators-online/images/Nintendo/GameCube')
			},
			'Interface' : {
				'ConfirmStop' : False,
				'UsePanicHandlers' : False, # Turn off panic handlers
				'OnScreenDisplayMessages' : True,
				'HideCursor' : False,
				'AutoHideCursor' : False,
				'MainWindowPosX' : 652,
				'MainWindowPosY' : 198,
				'MainWindowWidth' : 1241,
				'MainWindowHeight' : 774,
				'Language' : 0,
				'ShowToolbar' : True,
				'ShowStatusbar' : True,
				'ShowLogWindow' : False,
				'ShowLogConfigWindow' : False,
				'ExtendedFPSInfo' : False,
				'ThemeName40' : 'Clean'
			},
			'Hotkeys' : {
				'Open' : 79,
				'OpenModifier' : 2,
				'ChangeDisc' : 0,
				'ChangeDiscModifier' : 0,
				'RefreshList' : 0,
				'RefreshListModifier' : 0,
				'PlayPause' : 349,
				'PlayPauseModifier' : 0,
				'Stop' : 27,
				'StopModifier' : 0,
				'Reset' : 0,
				'ResetModifier' : 0,
				'FrameAdvance' : 0,
				'FrameAdvanceModifier' : 0,
				'StartRecording' : 0,
				'StartRecordingModifier' : 0,
				'PlayRecording' : 0,
				'PlayRecordingModifier' : 0,
				'ExportRecording' : 0,
				'ExportRecordingModifier' : 0,
				'Readonlymode' : 0,
				'ReadonlymodeModifier' : 0,
				'ToggleFullscreen' : 13,
				'ToggleFullscreenModifier' : 1,
				'Screenshot' : 348,
				'ScreenshotModifier' : 0,
				'Exit' : 0,
				'ExitModifier' : 0,
				'Wiimote1Connect' : 344,
				'Wiimote1ConnectModifier' : 1,
				'Wiimote2Connect' : 345,
				'Wiimote2ConnectModifier' : 1,
				'Wiimote3Connect' : 346,
				'Wiimote3ConnectModifier' : 1,
				'Wiimote4Connect' : 347,
				'Wiimote4ConnectModifier' : 1,
				'BalanceBoardConnect' : 348,
				'BalanceBoardConnectModifier' : 1,
				'ToggleIR' : 0,
				'ToggleIRModifier' : 0,
				'ToggleAspectRatio' : 0,
				'ToggleAspectRatioModifier' : 0,
				'ToggleEFBCopies' : 0,
				'ToggleEFBCopiesModifier' : 0,
				'ToggleFog' : 0,
				'ToggleFogModifier' : 0,
				'ToggleThrottle' : 9,
				'ToggleThrottleModifier' : 0,
				'IncreaseFrameLimit' : 0,
				'IncreaseFrameLimitModifier' : 0,
				'DecreaseFrameLimit' : 0,
				'DecreaseFrameLimitModifier' : 0,
				'FreelookIncreaseSpeed' : 49,
				'FreelookIncreaseSpeedModifier' : 4,
				'FreelookDecreaseSpeed' : 50,
				'FreelookDecreaseSpeedModifier' : 4,
				'FreelookResetSpeed' : 70,
				'FreelookResetSpeedModifier' : 4,
				'FreelookUp' : 69,
				'FreelookUpModifier' : 4,
				'FreelookDown' : 81,
				'FreelookDownModifier' : 4,
				'FreelookLeft' : 65,
				'FreelookLeftModifier' : 4,
				'FreelookRight' : 68,
				'FreelookRightModifier' : 4,
				'FreelookZoomIn' : 87,
				'FreelookZoomInModifier' : 4,
				'FreelookZoomOut' : 83,
				'FreelookZoomOutModifier' : 4,
				'FreelookReset' : 82,
				'FreelookResetModifier' : 4,
				'LoadStateSlot1' : 340,
				'LoadStateSlot1Modifier' : 0,
				'LoadStateSlot2' : 341,
				'LoadStateSlot2Modifier' : 0,
				'LoadStateSlot3' : 342,
				'LoadStateSlot3Modifier' : 0,
				'LoadStateSlot4' : 343,
				'LoadStateSlot4Modifier' : 0,
				'LoadStateSlot5' : 344,
				'LoadStateSlot5Modifier' : 0,
				'LoadStateSlot6' : 345,
				'LoadStateSlot6Modifier' : 0,
				'LoadStateSlot7' : 346,
				'LoadStateSlot7Modifier' : 0,
				'LoadStateSlot8' : 347,
				'LoadStateSlot8Modifier' : 0,
				'LoadStateSlot9' : 0,
				'LoadStateSlot9Modifier' : 0,
				'LoadStateSlot10' : 0,
				'LoadStateSlot10Modifier' : 0,
				'SaveStateSlot1' : 340,
				'SaveStateSlot1Modifier' : 4,
				'SaveStateSlot2' : 341,
				'SaveStateSlot2Modifier' : 4,
				'SaveStateSlot3' : 342,
				'SaveStateSlot3Modifier' : 4,
				'SaveStateSlot4' : 343,
				'SaveStateSlot4Modifier' : 4,
				'SaveStateSlot5' : 344,
				'SaveStateSlot5Modifier' : 4,
				'SaveStateSlot6' : 345,
				'SaveStateSlot6Modifier' : 4,
				'SaveStateSlot7' : 346,
				'SaveStateSlot7Modifier' : 4,
				'SaveStateSlot8' : 347,
				'SaveStateSlot8Modifier' : 4,
				'SaveStateSlot9' : 0,
				'SaveStateSlot9Modifier' : 0,
				'SaveStateSlot10' : 0,
				'SaveStateSlot10Modifier' : 0,
				'SelectStateSlot1' : 0,
				'SelectStateSlot1Modifier' : 0,
				'SelectStateSlot2' : 0,
				'SelectStateSlot2Modifier' : 0,
				'SelectStateSlot3' : 0,
				'SelectStateSlot3Modifier' : 0,
				'SelectStateSlot4' : 0,
				'SelectStateSlot4Modifier' : 0,
				'SelectStateSlot5' : 0,
				'SelectStateSlot5Modifier' : 0,
				'SelectStateSlot6' : 0,
				'SelectStateSlot6Modifier' : 0,
				'SelectStateSlot7' : 0,
				'SelectStateSlot7Modifier' : 0,
				'SelectStateSlot8' : 0,
				'SelectStateSlot8Modifier' : 0,
				'SelectStateSlot9' : 0,
				'SelectStateSlot9Modifier' : 0,
				'SelectStateSlot10' : 0,
				'SelectStateSlot10Modifier' : 0,
				'SaveSelectedSlot' : 0,
				'SaveSelectedSlotModifier' : 0,
				'LoadSelectedSlot' : 0,
				'LoadSelectedSlotModifier' : 0,
				'LoadLastState1' : 0,
				'LoadLastState1Modifier' : 0,
				'LoadLastState2' : 0,
				'LoadLastState2Modifier' : 0,
				'LoadLastState3' : 0,
				'LoadLastState3Modifier' : 0,
				'LoadLastState4' : 0,
				'LoadLastState4Modifier' : 0,
				'LoadLastState5' : 0,
				'LoadLastState5Modifier' : 0,
				'LoadLastState6' : 0,
				'LoadLastState6Modifier' : 0,
				'LoadLastState7' : 0,
				'LoadLastState7Modifier' : 0,
				'LoadLastState8' : 0,
				'LoadLastState8Modifier' : 0,
				'SaveFirstState' : 0,
				'SaveFirstStateModifier' : 0,
				'UndoLoadState' : 351,
				'UndoLoadStateModifier' : 0,
				'UndoSaveState' : 351,
				'UndoSaveStateModifier' : 4,
				'SaveStateFile' : 0,
				'SaveStateFileModifier' : 0,
				'LoadStateFile' : 0,
				'LoadStateFileModifier' : 0,
				'VolumeUp' : 0,
				'VolumeUpModifier' : 0,
				'VolumeDown' : 0,
				'VolumeDownModifier' : 0,
				'VolumeToggleMute' : 0,
				'VolumeToggleMuteModifier' : 0,
				'IncreaseDepth' : 0,
				'IncreaseDepthModifier' : 0,
				'DecreaseDepth' : 0,
				'DecreaseDepthModifier' : 0,
				'IncreaseConvergence' : 0,
				'IncreaseConvergenceModifier' : 0,
				'DecreaseConvergence' : 0,
				'DecreaseConvergenceModifier' : 0
			},
			'Display' : {
				'FullscreenResolution' : 'Auto',
				'Fullscreen' : False,
				'RenderToMain' : True, # Make the main window the only window
				'RenderWindowXPos' : 691,
				'RenderWindowYPos' : 466,
				'RenderWindowWidth' : 1102,
				'RenderWindowHeight' : 656,
				'RenderWindowAutoSize' : False,
				'KeepWindowOnTop' : False,
				'ProgressiveScan' : False,
				'DisableScreenSaver' : True,
				'ForceNTSCJ' : False
			},
			'GameList' : {
				'ListDrives' : False,
				'ListWad' : True,
				'ListWii' : True,
				'ListGC' : True,
				'ListJap' : True,
				'ListPal' : True,
				'ListUsa' : True,
				'ListAustralia' : True,
				'ListFrance' : True,
				'ListGermany' : True,
				'ListInternational' : True,
				'ListItaly' : True,
				'ListKorea' : True,
				'ListNetherlands' : True,
				'ListRussia' : True,
				'ListSpain' : True,
				'ListTaiwan' : True,
				'ListUnknown' : True,
				'ListSort' : 3,
				'ListSortSecondary' : 0,
				'ColorCompressed' : True,
				'ColumnPlatform' : True,
				'ColumnBanner' : True,
				'ColumnNotes' : True,
				'ColumnID' : False,
				'ColumnRegion' : True,
				'ColumnSize' : True,
				'ColumnState' : True,
			},
			'Core' : {
				'HLE_BS2' : False,
				'CPUCore' : 1,
				'Fastmem' : True,
				'CPUThread' : True,
				'DSPThread' : False,
				'DSPHLE' : True,
				'SkipIdle' : True,
				'DefaultISO' : '',
				'DVDRoot' : '',
				'Apploader' : '',
				'EnableCheats' : False,
				'SelectedLanguage' : 0,
				'DPL2Decoder' : False,
				'Latency' : 2,
				'MemcardAPath' : os.path.expanduser('~/Documents/Dolphin Emulator/GC/MemoryCardA.USA.raw'),
				'MemcardBPath' : os.path.expanduser('~/Documents/Dolphin Emulator/GC/MemoryCardB.USA.raw'),
				'SlotA' : 1,
				'SlotB' : 255,
				'SerialPort1' : 255,
				'BBA_MAC' : '',
				'SIDevice0' : 6,
				'SIDevice1' : 0,
				'SIDevice2' : 0,
				'SIDevice3' : 0,
				'WiiSDCard' : False,
				'WiiKeyboard' : False,
				'WiimoteContinuousScanning' : False,
				'WiimoteEnableSpeaker' : False,
				'RunCompareServer' : False,
				'RunCompareClient' : False,
				'FrameLimit' : 0x00000001,
				'FrameSkip' : 0x00000000,
				'GFXBackend' : 'OGL',
				'GPUDeterminismMode' : 'auto',
				'SyncOnSkipIdle' : True,
				'GameCubeAdapter' : True,
				'GameCubeAdapterThread' : True,
				'AgpCartAPath' : '',
				'AgpCartBPath' : '',
				'Overclock' : 1.000000,
				'OverclockEnable' : False
			},
			'Movie' : {
				'PauseMovie' : False,
				'Author' : '',
				'DumpFrames' : False,
				'ShowInputDisplay' : False
			},
			'DSP' : {
				'EnableJIT' : True,
				'DumpAudio' : False,
				'Backend' : 'XAudio2',
				'Volume' : 100,
				'CaptureLog' : False
			},
			'Input' : {
				'BackgroundInput' : False
			},
			'FifoPlayer' : {
				'LoopReplay' : True
			}
		}
		ini.WriteIniFile(ini_dolphin, config)

		# Create GCPadNew.ini
		ini_gc_pad = os.path.expanduser('~/Documents/Dolphin Emulator/Config/GCPadNew.ini')
		config = {
			'GCPad1' : {
				'Device' : 'XInput/0/Gamepad',
				'Buttons/A' : BUTTON_CODE_MAP[self.button_map['btn_a_dolphin']],
				'Buttons/B' : BUTTON_CODE_MAP[self.button_map['btn_b_dolphin']],
				'Buttons/X' : BUTTON_CODE_MAP[self.button_map['btn_x_dolphin']],
				'Buttons/Y' : BUTTON_CODE_MAP[self.button_map['btn_y_dolphin']],
				'Buttons/Z' : BUTTON_CODE_MAP[self.button_map['btn_z_dolphin']],
				'Buttons/Start' : BUTTON_CODE_MAP[self.button_map['btn_start_dolphin']],
				'Main Stick/Up' : BUTTON_CODE_MAP[self.button_map['btn_left_stick_up_dolphin']],
				'Main Stick/Down' : BUTTON_CODE_MAP[self.button_map['btn_left_stick_down_dolphin']],
				'Main Stick/Left' : BUTTON_CODE_MAP[self.button_map['btn_left_stick_left_dolphin']],
				'Main Stick/Right' : BUTTON_CODE_MAP[self.button_map['btn_left_stick_right_dolphin']],
				'Main Stick/Modifier' : '`Thumb L`', # FIXME: Make this L stick click
				'Main Stick/Modifier/Range' : '50.000000', # FIXME: is this OK to hard code at this value?
				'C-Stick/Up' : BUTTON_CODE_MAP[self.button_map['btn_right_stick_up_dolphin']],
				'C-Stick/Down' : BUTTON_CODE_MAP[self.button_map['btn_right_stick_down_dolphin']],
				'C-Stick/Left' : BUTTON_CODE_MAP[self.button_map['btn_right_stick_left_dolphin']],
				'C-Stick/Right' : BUTTON_CODE_MAP[self.button_map['btn_right_stick_right_dolphin']],
				'C-Stick/Modifier' : '`Thumb R`', # FIXME: Make this R stick click
				'C-Stick/Modifier/Range' : '50.000000', # FIXME: is this OK to hard code at this value?
				'Triggers/L' : BUTTON_CODE_MAP[self.button_map['btn_l_shoulder_dolphin']],
				'Triggers/R' : BUTTON_CODE_MAP[self.button_map['btn_r_shoulder_dolphin']],
				'Triggers/L-Analog' : BUTTON_CODE_MAP[self.button_map['btn_l_trigger_dolphin']],
				'Triggers/R-Analog' : BUTTON_CODE_MAP[self.button_map['btn_r_trigger_dolphin']],
				'D-Pad/Up' : BUTTON_CODE_MAP[self.button_map['btn_up_dolphin']],
				'D-Pad/Down' : BUTTON_CODE_MAP[self.button_map['btn_down_dolphin']],
				'D-Pad/Left' : BUTTON_CODE_MAP[self.button_map['btn_left_dolphin']],
				'D-Pad/Right' : BUTTON_CODE_MAP[self.button_map['btn_right_dolphin']],
			}
		}
		ini.WriteIniFile(ini_gc_pad, config)

		# Create gfx_opengl.ini
		ini_gfx_opengl = os.path.expanduser('~/Documents/Dolphin Emulator/Config/gfx_opengl.ini')
		config = {
			'Hardware' : {
				'VSync' : False,
				'Adapter' : 0
			},
			'Settings' : {
				'AspectRatio' : 0,
				'Crop' : False,
				'wideScreenHack' : False,
				'UseXFB' : False,
				'UseRealXFB' : False,
				'SafeTextureCacheColorSamples' : 128,
				'ShowFPS' : False,
				'LogRenderTimeToFile' : False,
				'OverlayStats' : False,
				'OverlayProjStats' : False,
				'DumpTextures' : False,
				'HiresTextures' : False,
				'DumpEFBTarget' : False,
				'FreeLook' : False,
				'UseFFV1' : False,
				'AnaglyphStereo' : False,
				'AnaglyphStereoSeparation' : 200,
				'AnaglyphFocalAngle' : 0,
				'EnablePixelLighting' : False,
				'FastDepthCalc' : True,
				'ShowEFBCopyRegions' : False,
				'MSAA' : 0,
				'EFBScale' : 2,
				'TexFmtOverlayEnable' : False,
				'TexFmtOverlayCenter' : False,
				'Wireframe' : False,
				'DstAlphaPass' : False,
				'DisableFog' : False,
				'EnableShaderDebugging' : False,
				'BorderlessFullscreen' : False
			},
			'Enhancements' : {
				'ForceFiltering' : False,
				'MaxAnisotropy' : 0,
				'PostProcessingShader' : '',
				'StereoMode' : 0,
				'StereoDepth' : 20,
				'StereoConvergence' : 20,
				'StereoSwapEyes' : False
			},
			'Hacks' : {
				'EFBAccessEnable' : True,
				'EFBCopyEnable' : True,
				'EFBToTextureEnable' : True,
				'EFBScaledCopy' : True,
				'EFBCopyCacheEnable' : False,
				'EFBEmulateFormatChanges' : False
			}
		}
		ini.WriteIniFile(ini_gfx_opengl, config)

		# Create Logger.ini
		ini_logger = os.path.expanduser('~/Documents/Dolphin Emulator/Config/Logger.ini')
		config = {
			'LogWindow' : {
				'x' : 400,
				'y' : 600,
				'pos' : 2
			},
			'Options' : {
				'Font' : 0,
				'WrapLines' : False
			}
		}
		ini.WriteIniFile(ini_logger, config)

		# Create WiimoteNew.ini
		ini_wiimote = os.path.expanduser('~/Documents/Dolphin Emulator/Config/WiimoteNew.ini')
		config = {
			'Wiimote1' : {
				'Source' : 1
			},
			'Wiimote2' : {
				'Source' : 0
			},
			'Wiimote3' : {
				'Source' : 0
			},
			'Wiimote4' : {
				'Source' : 0
			},
			'BalanceBoard' : {
				'Source' : 0
			}
		}
		ini.WriteIniFile(ini_wiimote, config)

	def run(self, path, binary):
		self._setup_configs()

		os.chdir("emulators/Dolphin-x64/")

		# Figure out if it is running a game or not
		command = None
		full_screen = False
		if path and binary:
			game_path = self.goodJoin("../../", path + '/' + binary)
			command = '"Dolphin.exe" --batch --exec="' + game_path + '"'
			full_screen = True
		else:
			command = '"Dolphin.exe" --batch'
			full_screen = False

		# Run the game
		runner = emu_runner.EmuRunner(command, 'Dolphin 4.0', full_screen, full_screen_alt_enter=True)
		runner.run()
		os.chdir("../..")

