
var db = {};
var socket = null;

// FIXME: The way we construct these divs dynamically is terrible. Replace with templates.
function make_game_icon(console_name, name, data, i) {
	// Create the icon
	var text = "" +
			"<a href=\"#dialog_" + name + "\" id=\"preview_" + i + "\">";
			
	if(data["binary"])
		text += "<img src=\"" + data["path"] + "00000000.png\" />";
	else
		text += "<img src=\"" + data["path"] + "00000000.png\" class=\"blackAndWhite\" />";

	text += "<br />" + 
		name + "</a>";
	var d = document.createElement('div');
	d.className = "gameIcon";
	d.innerHTML = text;
	document.getElementById('game_selector').appendChild(d);

	// Create the dialog
	var text = "" +
	"<div>" +
	"	<a href=\"#closeGameDialog\" class=\"closeGameDialog\">X</a>" + 
	"	<h2>" + name + "</h2>" + 
	"	<img src=\"" + data["path"] + "00000000.png\" />" +
	"	<input id=\"btn_" + i + "\" type=\"button\" value=\"play\" \>" +
	"	<br />";

	$.each(data["images"], function(n, image) {
		if(n != 0)
			text += "	<img src=\"" + data["path"] + image + "\" />";
	});

	text += "</div>";

	var d = document.createElement('div');
	d.id = "dialog_" + name;
	d.className = "gameDialog";
	d.innerHTML = text;
	document.getElementById('game_dialogs').appendChild(d);

	// Have the dialog play button launch the game
	var btn = $("#btn_" + i);
	btn.on('click', function() {
		var message = {
			'action' : 'play',
			'name' : name,
			'path' : data['path'],
			'binary' : data['binary'],
			'console' : console_name,
			'bios' : data['bios']
		}
		var message = JSON.stringify(message);
		socket.send(message);
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

function on_search() {
	var search_text = $('#search_text');

	// Get the words to search for
	var search_raw = search_text.val();
///*
	// Skip empty searches
	if(search_raw.length == 0) {
		var i = 0;
		$.each(db, function(console_name, console_data) {
			// Add console name as header
			var d = document.createElement('h1');
			d.innerHTML = console_name;
			d.style.clear = "both";
			document.getElementById('game_selector').appendChild(d);

			$.each(console_data, function(name, data) {
				make_game_icon(console_name, name, data, i);
				++i;
			});
		});
		return;
	}
//*/
///*
	// Match game genre
	var match_genre_db = [];
	var lower_search = search_raw.toLowerCase();
	$.each(db, function(console_name, console_data) {
		$.each(console_data, function(name, data) {
			if('genre' in data && data['genre'].toLowerCase() == lower_search) {
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
	$.each(db, function(console_name, console_data) {
		$.each(console_data, function(name, data) {
			// Skip if game was found in the genre search
			var already_searched = false;
			$.each(match_genre_db, function(n, gname) {
				if(name.toLowerCase() == gname.toLowerCase()) {
					already_searched = true;
					return false;
				}
			});
			if(already_searched)
				return false;

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

	$.each(db, function(console_name, console_data) {
		$.each(console_data, function(name, data) {

			// Skip if game was found in whole search
			var already_searched = false;
			$.each(match_whole_db, function(n, gname) {
				if(name.toLowerCase() == gname.toLowerCase()) {
					already_searched = true;
					return false;
				}
			});
			if(already_searched)
				return false;

			var game_words = get_searchable_words(name);

			// Count how many words match the search
			var match_count = 0;
			$.each(search_words, function(i, search_word) {
				$.each(game_words, function(j, game_word) {
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

	$.each(db, function(console_name, console_data) {
		$.each(console_data, function(name, data) {
			// Skip if game was found in words search
			var already_searched = false;
			$.each(match_words_db, function(gname, gcount) {
				if(name.toLowerCase() == gname.toLowerCase()) {
					already_searched = true;
					return false;
				}
			});
			if(already_searched)
				return false;

			var game_words = get_searchable_words(name);

			// Count how many words match the search
			var match_count = 0;
			$.each(search_words, function(i, search_word) {
				$.each(game_words, function(j, game_word) {
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

	// Clear the old icons
	document.getElementById('game_selector').innerHTML = "";

	// Create new icons from the search
	var i = 0;
	$.each(db, function(console_name, console_data) {
		// Add console name as header
		var d = document.createElement('h1');
		d.innerHTML = console_name;
		d.style.clear = "both";
		document.getElementById('game_selector').appendChild(d);

		$.each(console_data, function(name, data) {
///*
			// Genre matches
			$.each(match_genre_db, function(n, gname) {
				if(name == gname)
					make_game_icon(console_name, name, data, i);
			});
//*/
///*
			// Whole matches
			$.each(match_whole_db, function(n, gname) {
				if(name == gname)
					make_game_icon(console_name, name, data, i);
			});
//*/
///*
			// Word matches
			$.each(match_words_db, function(gname, gcount) {
				if(name == gname)
					make_game_icon(console_name, name, data, i);
			});
//*/
///*
			// Part matches
			$.each(match_parts_db, function(gname, gcount) {
				if(name == gname)
					make_game_icon(console_name, name, data, i);
			});
//*/
			++i;
		});
	});
}

function setup_websocket() {
	var host = "ws://localhost:9090/ws";
	socket = new WebSocket(host);

	// event handlers for websocket
	if(socket) {
		socket.onopen = function() {
			$("#not_connected").hide();
		}

		socket.onmessage = function(msg) {
			showServerResponse(msg.data);
		}

		socket.onclose = function() {
			$("#not_connected").show();
		}
	} else {
		console.log("invalid socket");
	}

	function showServerResponse(txt) {
		if(txt == "playing") {
			
		} else {
			var p = document.createElement('p');
			p.innerHTML = txt;
			document.getElementById('output').appendChild(p);
		}
	}


}
