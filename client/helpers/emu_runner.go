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
	"emu_archive/client/win32"
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
}

func (self *EmuRunner) Setup(command CommandWithArgs, emu_title_bar_text string, full_screen bool, full_screen_alt_enter bool) {
	self.emu_title_bar_text = emu_title_bar_text
	self.command = command
	self.full_screen = full_screen
	self.full_screen_alt_enter = full_screen_alt_enter
	//self.emu_proc = nil
}

func (self *EmuRunner) Run() {
	// 1/10th of a second
	wait_time := time.Millisecond * 100.0

	// Start the program
	self.emu_proc = exec.Command(self.command.name, self.command.args...)
	var std_out bytes.Buffer
	var std_err bytes.Buffer
	self.emu_proc.Stdout = &std_out
	self.emu_proc.Stderr = &std_err
	err := self.emu_proc.Start()
	if err != nil {
		fmt.Printf("Failed to start running the command: %s\r\n", err)
		log.Fatal(err)
	}

	// Wait for the program's window to actually be created
	var hwnd win32.HWND
	var title string
	time.Sleep(wait_time)
	for {
		fmt.Printf("Waiting for emulator window to appear ...\r\n")
		// Look through all the windows and find the one with the title bar text we want
		hwnd, title = win32.FindWindowWithTitleText(self.emu_title_bar_text)

		// Sleep for a bit if the window was not found
		if title == "" {
			time.Sleep(time.Second)
		} else {
			break
		}
	}

	// Show the window if it is minimized
	time.Sleep(wait_time)
	win32.ShowWindow(hwnd, true)
	win32.SetWindowPos(hwnd, win32.HWND_TOPMOST, 0, 0, 0,0, win32.SWP_NOMOVE | win32.SWP_NOSIZE)
	win32.SetWindowPos(hwnd, win32.HWND_NOTOPMOST, 0, 0, 0,0, win32.SWP_NOMOVE | win32.SWP_NOSIZE)
	win32.SetActiveWindow(hwnd)
	//win32.SetForegroundWindow(hwnd)

	// Move the mouse to the window corner, click on it, and move the mouse to the corner
	time.Sleep(wait_time)
	rect := win32.GetWindowRect(hwnd)
	win32.SetCursorPos(rect.Left + 1, rect.Top + 1)
	win32.MouseEvent(win32.MOUSEEVENTF_LEFTDOWN, rect.Left, rect.Top, 0, 0)
	win32.MouseEvent(win32.MOUSEEVENTF_LEFTUP, rect.Left, rect.Top, 0, 0)
	win32.SetCursorPos(0, 0)

	// Fullscreening the emu window with alt + enter if needed
	if self.full_screen && self.full_screen_alt_enter {
		time.Sleep(wait_time)
		win32.KeybdEvent(win32.VK_MENU, 0, 0, 0)
		win32.KeybdEvent(win32.VK_RETURN, 0, 0, 0)
		time.Sleep(time.Second * 2)
		win32.KeybdEvent(win32.VK_RETURN, 0, win32.KEYEVENTF_KEYUP, 0)
		win32.KeybdEvent(win32.VK_MENU, 0, win32.KEYEVENTF_KEYUP, 0)
	}
}

func (self *EmuRunner) Stop() string {
	//output := self.emu_proc.stdout.read()
	return "FIXME: Read the program output here"
}

