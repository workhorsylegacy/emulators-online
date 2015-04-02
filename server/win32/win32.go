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

package win32

import (
	// #include <wtypes.h>
	// #include <winable.h>

	"strings"

	"C"
	"syscall"
	"unsafe"
)

type (
	HANDLE uintptr
	HWND HANDLE
	HRESULT int32
)

type BROWSEINFO struct {
	Owner        HWND
	Root         *uint16
	DisplayName  *uint16
	Title        *uint16
	Flags        uint32
	CallbackFunc uintptr
	LParam       uintptr
	Image        int32
}

var (
	moduser32                         = syscall.NewLazyDLL("user32.dll")
	procGetWindowTextLength           = moduser32.NewProc("GetWindowTextLengthW")
	procGetWindowText                 = moduser32.NewProc("GetWindowTextW")
	procEnumWindows                   = moduser32.NewProc("EnumWindows")
	procGetForegroundWindow           = moduser32.NewProc("GetForegroundWindow")
	procGetDesktopWindow              = moduser32.NewProc("GetDesktopWindow")

	modshell32                        = syscall.NewLazyDLL("shell32.dll")
	procSHBrowseForFolder             = modshell32.NewProc("SHBrowseForFolderW")
	procSHGetPathFromIDList           = modshell32.NewProc("SHGetPathFromIDListW")
)

func GetWindowTextLength(hwnd HWND) int {
	ret, _, _ := procGetWindowTextLength.Call(uintptr(hwnd))
	return int(ret)
}

func GetWindowText(hwnd HWND) string {
	textLen := GetWindowTextLength(hwnd) + 1

	buf := make([]uint16, textLen)
	procGetWindowText.Call(
		uintptr(hwnd),
		uintptr(unsafe.Pointer(&buf[0])),
		uintptr(textLen))

	return syscall.UTF16ToString(buf)
}

func EnumWindows(enumFunc uintptr, lparam uintptr) (err error) {
	r1, _, e1 := syscall.Syscall(procEnumWindows.Addr(), 2, uintptr(enumFunc), uintptr(lparam), 0)
	if r1 == 0 {
		if e1 != 0 {
			err = error(e1)
		} else {
			err = syscall.EINVAL
		}
	}
	return
}

func GetForegroundWindow() (HWND) {
	ret, _, _ := procGetForegroundWindow.Call()
	return HWND(ret)
}

func GetDesktopWindow() (HWND) {
	ret, _, _ := procGetDesktopWindow.Call()
	return HWND(ret)
}

func SHGetPathFromIDList(idl uintptr) string {
	buf := make([]uint16, 1024)
	procSHGetPathFromIDList.Call(
		idl,
		uintptr(unsafe.Pointer(&buf[0])))

	return syscall.UTF16ToString(buf)
}

func SHBrowseForFolder(bi *BROWSEINFO) uintptr {
	ret, _, _ := procSHBrowseForFolder.Call(uintptr(unsafe.Pointer(bi)))
	return ret
}

func FindWindowWithTitleText(title_text string) (HWND, string) {
	// Get the handles of all the windows
	var res []HWND
	cb := syscall.NewCallback(func(h HWND, p uintptr) uintptr {
		res = append(res, h)
		return 1
	})
	EnumWindows(cb, 0)

	// Find the window with the desired title bar text
	for _, hwnd := range res {
		title := GetWindowText(hwnd)
		if strings.Contains(title, title_text) {
			return hwnd, title
		}
	}
	return 0, ""
}

