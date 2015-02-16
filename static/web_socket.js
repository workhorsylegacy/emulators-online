
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
