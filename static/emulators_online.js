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


var g_db = {};
var g_user_id = null;
var g_is_localhost = (["127.0.0.1", "localhost"].indexOf(document.location.hostname.toLowerCase()) != -1);

function assert_os_and_browser_requirements() {
	var errors = [];

	// Get the user agent
	var agent = navigator.userAgent.toLowerCase();

	// Show an alert if not on Windows
	if (agent.indexOf('windows') == -1) {
		errors.push('It only works on Windows.');
	}

	// Show an alert if not on a good browser
	if (agent.indexOf('firefox') == -1 && agent.indexOf('chrome') == -1) {
		errors.push('It only works in Firefox, Chrome, Opera or Edge browsers.');
	}

	// Check for localStorage
	if (!("localStorage" in window)) {
		errors.push("Your browser does not support localStorage.");
	}

	// Check for WebSockets
	// NOTE: IE 11 says it supports WebSockets, but it does not follow the specification
	if (!("WebSocket" in window) || agent.indexOf('trident') != -1) {
		errors.push("Your browser does not support WebSockets.");
	}

	// Check for Gamepads
	if (!("getGamepads" in navigator)) {
		errors.push("Your browser does not support Gamepads.");
	}
/*
	// Check for WebRTC
	if (!("RTCPeerConnection" in window) && !("mozRTCPeerConnection" in window) && !("webkitRTCPeerConnection" in window)) {
		errors.push("Your browser does not support WebRTC.");
	}
*/
	// Show an error message it features are missing
	if (errors.length) {
		var error_message = "This application will not run correctly!\r\n";
		for(var i=0; i<errors.length; ++i) {
			error_message += i+1 + ". " + errors[i] + "\r\n";
		}
		alert(error_message);
	}
}

function setup_user_id() {
	// Generate a random user id and store it in localStorage
	if (localStorage.getItem("g_user_id") == null) {
		g_user_id = generate_random_user_id();
		localStorage.setItem("g_user_id", g_user_id);
	// Or return the user id if already there
	} else {
		g_user_id = localStorage.getItem("g_user_id");
	}
	console.log("g_user_id: " + g_user_id);
}

function generate_random_user_id() {
	// Get a 20 character user id
	var code_table = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
	var user_id = "";
	for (var i = 0; i < 20; ++i) {
		// Get a random number between 0 and 35
		var num = Math.floor((Math.random() * 36));

		// Get the character that corresponds to the number
		user_id += code_table[num];
	}

	return user_id;
}

// FIXME: The way we construct these divs dynamically is terrible. Replace with templates.
function make_game_icon(console_name, name, data, i) {
	// Create the icon
	var text = "" +
			"<a href=\"#dialog_" + name + "\" id=\"preview_" + console_name + "_" + i + "\">";

	if(data["binary"])
		text += "<img src=\"" + data["path"] + "title_small.png\" />";

	text += "<br />" + 
		name + "</a>";

	var d = document.createElement('div');
	d.className = "game_icon";
	d.innerHTML = text;
	document.getElementById('game_selector').appendChild(d);

	var btn = $("#preview_" + console_name + "_" + i);
	btn.on('click', function() {
		// Create the dialog
		var text = "" +
		"<div>" +
		"	<a href=\"#close_game_dialog\" class=\"close_game_dialog\">X</a>" + 
		"	<h2>" + name + "</h2>" + 
		"	<img src=\"" + data["path"] + "title_big.png\" />" +
		"	<input id=\"btn_" + console_name + "_" + i + "\" type=\"button\" value=\"play\" \>" +
		"	<br />";

		$.each(data["images"], function(n, image) {
			console.log(image);
			if(n != 0)
				text += "	<img src=\"" + image + "\" />";
		});

		text += "</div>";

		var d = document.createElement('div');
		d.id = "dialog_" + name;
		d.className = "game_dialog";
		d.innerHTML = text;
		document.getElementById('game_dialogs').innerHTML = "";
		document.getElementById('game_dialogs').appendChild(d);


		// Have the dialog play button launch the game
		var btn = $("#btn_" + console_name + "_" + i);
		btn.on('click', function() {
			var message = {
				'action' : 'play',
				'name' : name,
				'path' : data['path'],
				'binary' : data['binary'],
				'console' : console_name,
				'bios' : data['bios']
			}
			web_socket_send_data(message);
		});
	});
}

function get_searchable_words(search_string) {
	// Get all the words in the name that are at least 3 characters long
	var all_words = search_string.toLowerCase().match(/\S+/g);
	var search_words = [];
	$.each(all_words, function(i, word) {
		if(word.length > 2) {
			search_words.push(word.toLowerCase());
		}
	});

	return search_words;
}

function on_search(evt) {
	var search_text = $('#search_text');

	// Clear the old icons
	document.getElementById('game_selector').innerHTML = "";

	// If there are no games, tell the user to add some
	var total_games = 0;
	$.each(g_db, function(console_name, console_data) {
		total_games += Object.keys(console_data).length;
	});
	if(total_games == 0) {
		document.getElementById('game_selector').innerHTML = "<h2>There are no games. You can add games on the configure page.</h2>";
		return;
	}

	// Get the words to search for
	var search_raw = search_text.val();
///*
	// Skip empty searches
	if(search_raw.length == 0) {
		var i = 0;
		var console_names = Object.keys(g_db);
		console_names.sort();
		$.each(console_names, function(i, console_name) {
			// Skip empty consoles
			var console_data = g_db[console_name];
			if(Object.keys(console_data).length == 0) {
				return true;
			}

			// Add console name as header
			var d = document.createElement('h1');
			d.innerHTML = console_name;
			d.style.clear = "both";
			document.getElementById('game_selector').appendChild(d);

			//if(console_data != null) {
				var names = $.map(console_data, function(key, value) {return value;});
				names.sort();
				$.each(names, function(j, name) {
					var data = console_data[name];
					make_game_icon(console_name, name, data, i);
					++i;
				});
			//}
		});
		return;
	}
//*/
///*
	// Match game developer
	var match_developer_db = [];
	var lower_search = search_raw.toLowerCase();
	var console_names = Object.keys(g_db);
	console_names.sort();
	$.each(console_names, function(i, console_name) {
		// Skip empty consoles
		var console_data = g_db[console_name];
		if(Object.keys(console_data).length == 0) {
			return true;
		}

		var names = $.map(console_data, function(key, value) {return value;});
		names.sort();
		$.each(names, function(j, name) {
			var data = console_data[name];
			if('developer' in data && data['developer'] && data['developer'].toLowerCase() == lower_search) {
				//console.log(name + " : " + data['developer']);
				match_developer_db.push(name);
			}
		});
	});
//*/
///*
	// Match game publisher
	var match_publisher_db = [];
	var lower_search = search_raw.toLowerCase();
	var console_names = Object.keys(g_db);
	console_names.sort();
	$.each(console_names, function(i, console_name) {
		// Skip empty consoles
		var console_data = g_db[console_name];
		if(Object.keys(console_data).length == 0) {
			return true;
		}

		var names = $.map(console_data, function(key, value) {return value;});
		names.sort();
		$.each(names, function(j, name) {
			var data = console_data[name];
			if('developer' in data && data['developer'] && data['developer'].toLowerCase() == lower_search) {
				match_publisher_db.push(name);
			}
		});
	});
//*/
///*
	// Match game genre
	var match_genre_db = [];
	var lower_search = search_raw.toLowerCase();
	var console_names = Object.keys(g_db);
	console_names.sort();
	$.each(console_names, function(i, console_name) {
		// Skip empty consoles
		var console_data = g_db[console_name];
		if(Object.keys(console_data).length == 0) {
			return true;
		}

		var names = $.map(console_data, function(key, value) {return value;});
		names.sort();
		$.each(names, function(j, name) {
			var data = console_data[name];
			if('genre' in data && data['genre'] && data['genre'].toLowerCase() == lower_search) {
				//console.log(name + " : " + data['genre']);
				match_genre_db.push(name);
			}
		});
	});
//*/
///*
	// Match whole game name
	var match_whole_db = [];
	var lower_search = search_raw.toLowerCase();
	var console_names = Object.keys(g_db);
	console_names.sort();
	$.each(console_names, function(i, console_name) {
		// Skip empty consoles
		var console_data = g_db[console_name];
		if(Object.keys(console_data).length == 0) {
			return true;
		}

		var names = $.map(console_data, function(key, value) {return value;});
		names.sort();
		$.each(names, function(j, name) {
			var data = console_data[name];
			if(name.toLowerCase() == lower_search) {
				match_whole_db.push(name);
			}
		});
	});
//*/
///*
	// Match some words in game name
	var match_words_db = {};
	var search_words = get_searchable_words(search_raw);

	var console_names = Object.keys(g_db);
	console_names.sort();
	$.each(console_names, function(i, console_name) {
		// Skip empty consoles
		var console_data = g_db[console_name];
		if(Object.keys(console_data).length == 0) {
			return true;
		}

		var names = $.map(console_data, function(key, value) {return value;});
		names.sort();
		$.each(names, function(j, name) {
			var data = console_data[name];
			var game_words = get_searchable_words(name);

			// Count how many words match the search
			var match_count = 0;
			$.each(search_words, function(k, search_word) {
				$.each(game_words, function(l, game_word) {
					if(game_word == search_word) {
						++match_count;
					}
				});
			});
			if(match_count > 0) {
				// Init the hash if empty
				if(!(name in match_words_db))
					match_words_db[name] = 0;

				// Save the match count if bigger
				if(match_count > match_words_db[name])
					match_words_db[name] = match_count;
			}
		});
	});
//*/
///*
	// Match parts of words in game name
	var match_parts_db = {};
	var search_words = get_searchable_words(search_raw);

	var console_names = Object.keys(g_db);
	console_names.sort();
	$.each(console_names, function(i, console_name) {
		// Skip empty consoles
		var console_data = g_db[console_name];
		if(Object.keys(console_data).length == 0) {
			return true;
		}

		var names = $.map(console_data, function(key, value) {return value;});
		names.sort();
		$.each(names, function(j, name) {
			var data = console_data[name];
			var game_words = get_searchable_words(name);

			// Count how many words match the search
			var match_count = 0;
			$.each(search_words, function(k, search_word) {
				$.each(game_words, function(l, game_word) {
					if(search_word.indexOf(game_word) > -1 || game_word.indexOf(search_word) > -1) {
						++match_count;
					}
				});
			});
			if(match_count > 0) {
				// Init the hash if empty
				if(!(name in match_parts_db))
					match_parts_db[name] = 0;

				// Save the match count if bigger
				if(match_count > match_parts_db[name])
					match_parts_db[name] = match_count;
			}
		});
	});
//*/

	// Create new icons from the search
	var i = 0;
	var console_names = Object.keys(g_db);
	console_names.sort();
	$.each(console_names, function(i, console_name) {
		// Skip empty consoles
		var console_data = g_db[console_name];
		if(Object.keys(console_data).length == 0) {
			return true;
		}

		var names = $.map(console_data, function(key, value) {return value;});
		names.sort();

		// Add console name as header
		var d = document.createElement('h1');
		d.innerHTML = console_name;
		d.style.clear = "both";
		document.getElementById('game_selector').appendChild(d);

		$.each(names, function(j, name) {
			var is_match = false;
///*
			// Developer matches
			$.each(match_developer_db, function(k, gname) {
				if(name == gname) {
					is_match = true;
					return false;
				}
			});
//*/
///*
			// Publisher matches
			$.each(match_publisher_db, function(k, gname) {
				if(name == gname) {
					is_match = true;
					return false;
				}
			});
//*/
///*
			// Genre matches
			$.each(match_genre_db, function(k, gname) {
				if(name == gname) {
					is_match = true;
					return false;
				}
			});
//*/
///*
			// Whole matches
			$.each(match_whole_db, function(k, gname) {
				if(name == gname) {
					is_match = true;
					return false;
				}
			});
//*/
///*
			// Word matches
			$.each(match_words_db, function(gname, gcount) {
				if(name == gname) {
					is_match = true;
					return false;
				}
			});
//*/
///*
			// Part matches
			$.each(match_parts_db, function(gname, gcount) {
				if(name == gname) {
					is_match = true;
					return false;
				}
			});
//*/
			if(is_match) {
				var data = console_data[name];
				make_game_icon(console_name, name, data, i);
			}

			++i;
		});
	});
}


