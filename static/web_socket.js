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


var socket = null;

function socket_send_data(message) {
	message = JSON.stringify(message);
	socket.send(message);
}

function setup_websocket(on_data) {
	var host = "ws://localhost:9090/ws";
	socket = null;

	try {
		socket = new WebSocket(host);
	} catch(e) { 
		socket = null;
	}

	// event handlers for websocket
	if(socket) {
		socket.onopen = function() {
			$("#error_header").hide();
			$("#search_header").show();
		};

		socket.onmessage = function(msg) {
			var data = JSON.parse(msg.data);
			on_data(data);
		};

		socket.onclose = function() {
			$("#error_header").show();
			$("#search_header").hide();

			// Re-connect again in 3 seconds
			setTimeout(function() {
				setup_websocket(on_data);
			}, 3000);
		};

		socket.onerror = function(err) {
		};
	} else {
		console.log("invalid socket");
	}
}
