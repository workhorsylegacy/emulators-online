

import os, sys

import ini
import emu_runner

def goodJoin(path_a, path_b):
	path = path_a + path_b
	path = os.path.abspath(path)
	path = path.replace("\\", "/")
	return path

def setup_pad():
	config = {
		'JOY0_0' : {
			'UP' : 805306368,
			'DOWN' : 805306369,
			'LEFT' : 805306370,
			'RIGHT' : 805306371,
			'A' : 805306380,
			'B' : 805306381,
			'C' : 0,
			'D' : 0,
			'X' : 805306382,
			'Y' : 805306383,
			'Z' : 0,
			'LTRIG' : 1342177280,
			'RTRIG' : 1342177536,
			'START' : 805306372,
			'S1UP' : -1879047680,
			'S1DOWN' : -1879047424,
			'S1LEFT' : -1879048192,
			'S1RIGHT' : -1879047936,
			'S2UP' : -1879046656,
			'S2DOWN' : -1879046400,
			'S2LEFT' : -1879047168,
			'S2RIGHT' : -1879046912
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
	ini.write_ini_file('emulators/Demul/padDemul.ini', config)

	
def run(path, binary):
	# Setup SPU
	config = {}
	config['main'] = {}
	config['main']['spuDisable'] = 'false'
	config['main']['cddaDisable'] = 'false'
	config['main']['dspDisable'] = 'false'
	config['main']['spuRecord'] = 'false'
	config['main']['bufSize'] = 2048
	ini.write_ini_file('emulators/Demul/spuDemul.ini', config)


	# Setup Pad
	setup_pad()


	# Setup Net
	config = {}
	config['main'] = {}
	config['main']['netEnable'] = 'false'
	config['main']['swapDisable'] = 'false'
	config['main']['NameOverride'] = ''
	ini.write_ini_file('emulators/Demul/netDemul.ini', config)


	# Setup GDR Image
	config = {}
	config['main'] = {}
	config['main']['imageFileName'] = ''
	config['main']['openDialog'] = 'true'
	ini.write_ini_file('emulators/Demul/gdrImage.ini', config)


	# Setup DirectX
	config = {}
	config['main'] = {}
	config['main']['Vsync'] = 0
	config['main']['AutoSort'] = 0
	config['main']['NetworkSort'] = 0
	config['main']['OModifier'] = 0
	config['main']['TModifier'] = 0
	config['main']['UseFullscreen'] = 0
	config['main']['rotate'] = 0
	config['main']['aspect'] = 1
	config['main']['scaling'] = 1
	config['main']['MaxLayers'] = 32
	config['main']['NotAutoRotate'] = 0

	config['resolution'] = {}
	config['resolution']['Width'] = 640
	config['resolution']['Height'] = 480

	config['shaders'] = {}
	config['shaders']['usePass1'] = 0
	config['shaders']['usePass2'] = 0
	config['shaders']['shaderPass1'] = ''
	config['shaders']['shaderPass2'] = ''
	ini.write_ini_file('emulators/Demul/gpuDX11.ini', config)


	# Setup Demul
	config = {}
	config['files'] = {}
	config['files']['nvram'] = os.path.abspath('emulators/Demul/nvram/')
	config['files']['romsPathsCount'] = 1
	config['files']['roms0'] = os.path.abspath('emulators/Demul/roms/')

	config['PORTD'] = {}
	config['PORTD']['device'] = -1
	config['PORTD']['port4'] = -1
	config['PORTD']['port2'] = -1
	config['PORTD']['port3'] = -1
	config['PORTD']['port0'] = -1
	config['PORTD']['port1'] = -1

	config['PORTB'] = {}
	config['PORTB']['device'] = -1
	config['PORTB']['port4'] = -1
	config['PORTB']['port2'] = -1
	config['PORTB']['port3'] = -1
	config['PORTB']['port0'] = -1
	config['PORTB']['port1'] = -1

	config['PORTC'] = {}
	config['PORTC']['device'] = -1
	config['PORTC']['port4'] = -1
	config['PORTC']['port2'] = -1
	config['PORTC']['port3'] = -1
	config['PORTC']['port0'] = -1
	config['PORTC']['port1'] = -1

	config['PORTA'] = {}
	config['PORTA']['device'] = 16777216
	config['PORTA']['port4'] = -1
	config['PORTA']['port2'] = -1
	config['PORTA']['port3'] = -1
	config['PORTA']['port0'] = 234881024
	config['PORTA']['port1'] = 65536

	config['plugins'] = {}
	config['plugins']['gdr'] = 'gdrImage.dll'
	config['plugins']['spu'] = 'spuDemul.dll'
	config['plugins']['pad'] = 'padDemul.dll'
	config['plugins']['directory'] = os.path.abspath('emulators/Demul/plugins/')
	config['plugins']['gpu'] = 'gpuDX11.dll'
	config['plugins']['net'] = 'netDemul.dll'

	config['main'] = {}
	config['main']['windowY'] = 100
	config['main']['windowX'] = 100
	config['main']['VMUscreendisable'] = 'false'
	config['main']['dcBios'] = 3
	config['main']['region'] = 1
	config['main']['activateBBA'] = 'false'
	config['main']['cpumode'] = 1
	config['main']['hikaruBios'] = 1
	config['main']['naomiBiosAuto'] = 'true'
	config['main']['broadcast'] = 1
	config['main']['lastEmuRunMode'] = 0
	config['main']['naomifreq'] = 1
	config['main']['naomiLLEMIE'] = 'false'
	config['main']['timehack'] = 'true'
	config['main']['videomode'] = 768

	config['VMS'] = {}
	config['VMS']['VMSA4'] = ''
	config['VMS']['VMSA0'] = os.path.abspath('emulators/Demul/memsaves/vms00.bin')
	config['VMS']['VMSA1'] = ''
	config['VMS']['VMSA2'] = ''
	config['VMS']['VMSA3'] = ''
	config['VMS']['VMSC2'] = ''
	config['VMS']['VMSD4'] = ''
	config['VMS']['VMSD0'] = ''
	config['VMS']['VMSD2'] = ''
	config['VMS']['VMSD1'] = ''
	config['VMS']['VMSC3'] = ''
	config['VMS']['VMSD3'] = ''
	config['VMS']['VMSC0'] = ''
	config['VMS']['VMSB4'] = ''
	config['VMS']['VMSC4'] = ''
	config['VMS']['VMSC1'] = ''
	config['VMS']['VMSB1'] = ''
	config['VMS']['VMSB0'] = ''
	config['VMS']['VMSB3'] = ''
	config['VMS']['VMSB2'] = ''
	ini.write_ini_file('emulators/Demul/Demul.ini', config)


	# Get the DirectX version for the window title
	directx_dll = config['plugins']['gpu']
	directx_version = None
	if directx_dll == 'gpuDX11.dll':
		directx_version = 'gpuDX11hw'
	elif directx_dll == 'gpuDX10.dll':
		directx_version = 'gpuDX10hw'

	# Run the game
	os.chdir("emulators/Demul/")
	game_path = goodJoin("../../", path + '/' + binary)
	command = '"demul.exe" -run=dc -image="' + game_path + '"'
	runner = emu_runner.EmuRunner(command, directx_version, full_screen_alt_enter=True)
	runner.run()
	os.chdir("../..")

