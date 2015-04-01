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
	// Convert message to json
	message = JSON.stringify(message);

	// Convert json to base64
	message = btoa(message);

	var header = message.length.toString();
	message = header + ":" + message;
	console.log("sending message: " + message);

	// Send the message
	socket.send(message);
}

function setup_websocket(on_data, on_open_cb) {
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

			if(on_open_cb) {
				on_open_cb();
				on_open_cb = null;
			}
		};

		socket.onmessage = function(msg) {
			// Read the message
			var message =  msg.data;
			console.log("received message: " + message);

			// Get the length and data
			var chunks = message.split(":");
			var length = chunks[0];
			var data = chunks[1];
			console.log(data);

			// Convert the data to an object
			data = atob(data);
			data = JSON.parse(data);
			console.log(data);

			// Convert the actual data to an object
			//data['json_data'] = atob(data['json_data']);
			console.log(data);
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
