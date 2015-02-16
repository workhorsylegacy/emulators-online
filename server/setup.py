
from distutils.core import setup
import py2exe
import os
import base64

if os.path.isfile('static_files.py'):
	os.remove('static_files.py')

# Get all the static files and add them to a python file
data = {}
with open('../index.html', 'rb') as f:
	data['index.html'] = base64.b64encode(f.read())
	
with open('../configure.html', 'rb') as f:
	data['configure.html'] = base64.b64encode(f.read())

with open('../static/default.css', 'rb') as f:
	data['static/default.css'] = base64.b64encode(f.read())

with open('../static/emu_archive.js', 'rb') as f:
	data['static/emu_archive.js'] = base64.b64encode(f.read())

with open('../static/file_uploader.js', 'rb') as f:
	data['static/file_uploader.js'] = base64.b64encode(f.read())

with open('../static/favicon.ico', 'rb') as f:
	data['static/favicon.ico'] = base64.b64encode(f.read())

with open('../static/input.js', 'rb') as f:
	data['static/input.js'] = base64.b64encode(f.read())

with open('../static/web_socket.js', 'rb') as f:
	data['static/web_socket.js'] = base64.b64encode(f.read())

with open('../static/jquery-2.1.3.min.js', 'rb') as f:
	data['static/jquery-2.1.3.min.js'] = base64.b64encode(f.read())

with open('static_files.py', 'wb') as f:
	f.write(
	"\r\n"
	+ "static_files = {\r\n")

	for file, content in data.items():
		f.write(
		"'" + file + "' : \"" + content + "\",\r\n")

	f.write(
	"}")

setup(
	options = {'py2exe': {'bundle_files': 1}},
	windows=['server.py'],
	zipfile=None
)
