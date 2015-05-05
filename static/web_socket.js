// Copyright (c) 2015, Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
// emulators-online is a HTML based front end for video game console emulators
// It uses the GNU AGPL 3 license
// It is hosted at: https://github.com/workhorsy/emulators-online
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.


var socket = null;

function web_socket_send_data(message) {
	// Convert message to json
	message = JSON.stringify(message);

	// Convert json to base64
	message = btoa(message);

	var header = message.length.toString();
	message = header + ":" + message;
	//console.log("sending message: " + message);

	// Send the message
	socket.send(message);
}

function setup_websocket(port, on_data, on_open_cb, on_close_cb) {
	var host = "ws://localhost:" + port.toString() + "/ws";
	socket = null;

	try {
		socket = new WebSocket(host);
	} catch(e) { 
		socket = null;
	}

	// event handlers for websocket
	if(socket) {
		socket.onopen = function() {
			if(on_open_cb) {
				on_open_cb();
			}
		};

		socket.onmessage = function(msg) {
			// Read the message
			var message =  msg.data;
			//console.log("received message: " + message);

			// Get the length and data
			var chunks = message.split(":");
			var length = chunks[0];
			var data = chunks[1];
			//console.log(data);

			// Convert the data to an object
			data = atob(data);
			data = JSON.parse(data);
			//console.log(data);

			// Convert the actual data to an object
			//console.log(data);
			on_data(data);
		};

		socket.onclose = function() {
			// Show the error page after 1 second, and start the reconnection loop
			// This prevents the error page from flickering on when we move pages
			setTimeout(function() {
				if(on_close_cb) {
					on_close_cb();
				}

				// Re-connect again in 3 seconds
				setTimeout(function() {
					setup_websocket(on_data);
				}, 3000);
			}, 1000);
		};

		socket.onerror = function(err) {
		};
	} else {
		console.log("invalid socket");
	}
}
