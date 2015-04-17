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

var db = {};


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
			socket_send_data(message);
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
	$.each(db, function(console_name, console_data) {
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
		var console_names = Object.keys(db);
		console_names.sort();
		$.each(console_names, function(i, console_name) {
			// Skip empty consoles
			var console_data = db[console_name];
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
	var console_names = Object.keys(db);
	console_names.sort();
	$.each(console_names, function(i, console_name) {
		// Skip empty consoles
		var console_data = db[console_name];
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
	var console_names = Object.keys(db);
	console_names.sort();
	$.each(console_names, function(i, console_name) {
		// Skip empty consoles
		var console_data = db[console_name];
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
	var console_names = Object.keys(db);
	console_names.sort();
	$.each(console_names, function(i, console_name) {
		// Skip empty consoles
		var console_data = db[console_name];
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
	var console_names = Object.keys(db);
	console_names.sort();
	$.each(console_names, function(i, console_name) {
		// Skip empty consoles
		var console_data = db[console_name];
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

	var console_names = Object.keys(db);
	console_names.sort();
	$.each(console_names, function(i, console_name) {
		// Skip empty consoles
		var console_data = db[console_name];
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

	var console_names = Object.keys(db);
	console_names.sort();
	$.each(console_names, function(i, console_name) {
		// Skip empty consoles
		var console_data = db[console_name];
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
	var console_names = Object.keys(db);
	console_names.sort();
	$.each(console_names, function(i, console_name) {
		// Skip empty consoles
		var console_data = db[console_name];
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


