

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

