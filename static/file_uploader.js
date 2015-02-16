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


var FileUploader = function(file_id, progress_percent_id, doneCB) {
	file_reader = null;
	progress_percent = document.getElementById(progress_percent_id);

	function abortRead() {
		file_reader.abort();
	}

	function onError(evt) {
		switch(evt.target.error.code) {
			case evt.target.error.NOT_FOUND_ERR:
				alert('File Not Found!');
				break;
			case evt.target.error.NOT_READABLE_ERR:
				alert('File is not readable');
				break;
			case evt.target.error.ABORT_ERR:
				break;
			default:
				alert('An error occurred reading this file.');
		};
	}

	function onAbort(evt) {
		alert('File read cancelled');
	}

	function onProgress(evt) {
		// evt is an ProgressEvent
		if (evt.lengthComputable) {
			var percentLoaded = Math.round((evt.loaded / evt.total) * 100);
			// Increase the progress bar length
			if (percentLoaded < 100) {
				progress_percent.textContent = percentLoaded + '%';
			}
		}
	}

	function onDone(evt) {
		// Set the progress bar to 100%
		progress_percent.textContent = '100%';

		doneCB(evt.target.result);
	}

	function handleFileSelect(evt) {
		// Reset the progress bar
		progress_percent.textContent = '0%';

		// Set all the callbacks
		file_reader = new FileReader();
		file_reader.onprogress = onProgress;
		file_reader.onload = onDone;
		file_reader.onerror = onError;
		file_reader.onabort = onAbort;

		// Read the file content
		file_reader.readAsBinaryString(evt.target.files[0]);
	}

	document.getElementById(file_id).addEventListener('change', handleFileSelect, false);
};

