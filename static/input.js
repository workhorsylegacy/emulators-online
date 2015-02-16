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



KEYBOARD_JS_CODE_MAP = {
	0 : 'none',
	27 : 'ESCAPE',
	49 : '1',
	50 : '2',
	51 : '3',
	52 : '4',
	53 : '5',
	54 : '6',
	55 : '7',
	56 : '8',
	57 : '9',
	48 : '0',
	109 : 'MINUS',
	187 : 'EQUALS',
	8 : 'BACKSPACE',
	9 : 'TAB',
	81 : 'Q',
	87 : 'W',
	69 : 'E',
	82 : 'R',
	84 : 'T',
	89 : 'Y',
	85 : 'U',
	73 : 'I',
	79 : 'O',
	80 : 'P',
	219 : 'LBRACKET',
	221 : 'RBRACKET',
	13 : 'RETURN',
	17 : 'LCONTROL',
	65 : 'A',
	83 : 'S',
	68 : 'D',
	70 : 'F',
	71 : 'G',
	72 : 'H',
	74 : 'J',
	75 : 'K',
	76 : 'L',
	186 : 'SEMICOLON',
	222 : 'APOSTROPHE',
	192 : 'GRAVE',
	16 : 'LSHIFT',
	220: 'BACKSLASH',
	90 : 'Z',
	88 : 'X',
	67 : 'C',
	86 : 'V',
	66 : 'B',
	78 : 'N',
	77 : 'M',
	188 : 'COMMA',
	190 : 'PERIOD',
	191 : 'SLASH',
	16 : 'RSHIFT',
	106 : 'MULTIPLY',
	18 : 'LMENU',
	32 : 'SPACE',
	20 : 'CAPITAL', // Caps Lock
	112 : 'F1',
	113 : 'F2',
	114 : 'F3',
	115 : 'F4',
	116 : 'F5',
	117 : 'F6',
	118 : 'F7',
	119 : 'F8',
	120 : 'F9',
	121 : 'F10',
	144 : 'NUMLOCK',
	145 : 'SCROLL',	
	103 : 'NUMPAD7',
	104 : 'NUMPAD8',
	105 : 'NUMPAD9',
	109 : 'SUBTRACT',
	100 : 'NUMPAD4',
	101 : 'NUMPAD5',
	102 : 'NUMPAD6',
	107 : 'ADD',
	97 : 'NUMPAD1',
	98 : 'NUMPAD2',
	99 : 'NUMPAD3',
	96 : 'NUMPAD0',
	110 : 'DECIMAL',
	122 : 'F11',
	123 : 'F12',
	/*
	'F13',
	'F14',
	'F15',
	'F16',
	'F17',
	'F18',
	'KANA',
	'F19',
	'CONVERT',
	'NOCONVERT',
	'YEN'# ¥
	'NUMPADEQUALS',
	'CIRCUMFLEX', # ^
	'AT', # @
	'COLON', # :
	'UNDERLINE', # _
	'KANJI',
	'STOP',
	'AX',
	'UNLABLED',
	13 : 'NUMPADENTER',
	17 : 'RCONTROL',
	'SECTION',
	'NUMPADCOMMA',
	111 : 'DIVIDE',
	'SYSRQ',
	*/
	18 : 'RMENU', // Right Menu/Alt
	//'FUNCTION',
	19 : 'PAUSE', 
	36 : 'HOME',
	38 : 'UP',
	33 : 'PRIOR', // Page Up
	37 : 'LEFT', // Left Arrow
	39 : 'RIGHT', // Right Arrow
	35 : 'END',
	40 : 'DOWN', // Down Arrow
	34 : 'NEXT', // Page Down
	45 : 'INSERT',
	46 : 'DELETE',
	91 : 'LMETA', // Left Meta/Super
	//'LWIN',
	//'RMETA', # Right Meta/Super
	//'RWIN',
	//'APPS',
	//'POWER',
	//'SLEEP'
};

var gamepad = null;

// Find already connected pads
$.each(navigator.getGamepads(), function(i, pad) {
	if(pad && pad.id) {
		gamepad = pad;
		console.log("Gamepad connected at index " + gamepad.index + ": " + gamepad.id + ". It has " + gamepad.buttons.length + " buttons and " + gamepad.axes.length + " axes.");
		return false;
	}
});

// Handle connecting and disconnecting pads
function gamepadHandler(e, connecting) {
	if (connecting) {
		gamepad = navigator.getGamepads()[e.gamepad.index];
		if(gamepad)
			console.log("Gamepad connected at index " + gamepad.index + ": " + gamepad.id + ". It has " + gamepad.buttons.length + " buttons and " + gamepad.axes.length + " axes.");
	} else {
		gamepad = null;
	}
}

window.addEventListener("gamepadconnected", function(e) { gamepadHandler(e, true); }, false);
window.addEventListener("gamepaddisconnected", function(e) { gamepadHandler(e, false); }, false);

var is_polling_buttons = false;

function start_polling_buttons(done_cb) {
	is_polling_buttons = true;

	// Check the pressed buttons every 300 ms
	var interval = setInterval(function() {
		var pressed_button = get_pressed_button();
		if(pressed_button != -1) {
			is_polling_buttons = false;
		}

		if(!is_polling_buttons) {
			done_cb(pressed_button);
			clearInterval(interval);
		}
	}, 100);

	// Stop checking after 5 seconds
	setTimeout(function() {
		is_polling_buttons = false;
	}, 5000);
}

function get_pressed_button() {
	var all_pads = navigator.getGamepads();
	if(all_pads.length < 1)
		return -1;

	gamepad = all_pads[0];

	if(gamepad == null || gamepad.buttons == null)
		return -1;

	for(var i in gamepad.buttons) {
		var button = gamepad.buttons[i];
		if(button) {
			if(typeof(button) == 'object') {
				if(button.pressed) {
					return 'button_' + i;
				}
			} else if(button) {
				return 'button_' + i;
			}
		}
	}

	for(var i in gamepad.axes) {
		var axis = gamepad.axes[i];
		var sign = axis > 0 ? '+' : '-';
		if(Math.abs(axis) > 0.5) {
			return 'axes_' + i + sign;
		}
	}

	return -1;
}
