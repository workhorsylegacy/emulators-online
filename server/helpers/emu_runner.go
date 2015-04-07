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

import (
	"os/exec"
	"bytes"
	"fmt"
	"time"
	"log"
)

type CommandWithArgs struct {
	name string
	args []string
}

type EmuRunner struct {
	emu_title_bar_text string
	command CommandWithArgs
	full_screen bool
	full_screen_alt_enter bool
	emu_proc *exec.Cmd
	foundWindows []string
}

func (self *EmuRunner) Setup(command CommandWithArgs, emu_title_bar_text string, full_screen bool, full_screen_alt_enter bool) {
	self.emu_title_bar_text = emu_title_bar_text
	self.command = command
	self.full_screen = full_screen
	self.full_screen_alt_enter = full_screen_alt_enter
	//self.emu_proc = nil
	//self.foundWindows = []
}

func (self *EmuRunner) Run() {
/*
	enumWindowFunc := func(hwnd, windowList) {
		text = win32gui.GetWindowText(hwnd)
		className = win32gui.GetClassName(hwnd)
		if text.find(self.emu_title_bar_text) >= 0 {
			windowList = windowList.Append((hwnd, text, className))
		}
	}
*/
	// 1/10th of a second
	wait_time := time.Millisecond * 100.0

	// Start the program
	self.emu_proc = exec.Command(self.command.name, self.command.args...)
	var out bytes.Buffer
	self.emu_proc.Stdout = &out
	err := self.emu_proc.Start()
	if err != nil {
		fmt.Printf("Failed to start running the command: %s\r\n", err)
		log.Fatal(err)
		
	}

	// Wait for the program's window to actually be created
	time.Sleep(wait_time)
	for {
		fmt.Printf("Waiting ...\r\n")
		// Look through all the windows and find the one with the title bar text we want
//		win32.EnumWindows(enumWindowFunc, self.foundWindows)

		// Sleep for a bit if the window was not found
		if len(self.foundWindows) < 1 {
			time.Sleep(time.Second)
		} else {
			break
		}
	}
/*
	// Focus the window
	time.Sleep(wait_time)
	for {
		fmt.Printf("Waiting ...\r\n")
		// Look through all the windows and find the one with the title bar text we want
		win32gui.EnumWindows(enumWindowFunc, self.foundWindows)

		if ! self.foundWindows {
			continue
		}

		// Focus the window
		got_window = False
		for hwnd, text, className in self.foundWindows {
			// Show the window if it is minimized
			time.Sleep(wait_time)
			win32gui.ShowWindow(hwnd, True)
			win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
			win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
			win32gui.SetActiveWindow(hwnd)
			//win32gui.SetForegroundWindow(hwnd)

			// Move the mouse to the window corner, click on it, and move the mouse to the corner
			time.Sleep(wait_time)
			x, y, w, h = win32gui.GetWindowRect(hwnd)
			win32api.SetCursorPos((x+1, y+1))
			win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
			win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
			win32api.SetCursorPos((0, 0))
			got_window = True
			break
		}
					
		if got_window {
			break
		}
	}

	// Fullscreening the emu window with alt + enter if needed
	if self.full_screen && self.full_screen_alt_enter {
		time.Sleep(wait_time)
		win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
		win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
		time.Sleep(time.Second(2))
		win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
		win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
	}
*/
}

func (self *EmuRunner) Stop() string {
	//output := self.emu_proc.stdout.read()
	return "FIXME: Read the program output here"
}

