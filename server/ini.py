
import os


def read_ini_file(file_path):
	with open(file_path, 'rb') as f:
		ini_data = f.read()

	config = {}

	# Read the ini file into a dictionary
	header = None
	for line in ini_data.splitlines():
		# Line is a header
		if '[' in line and ']' in line:
			header = line.split('[')[1].split(']')[0]
			config[header] = {}
			#print(header)
		# Line is a key value pair
		elif ' = ' in line:
			key, value = line.split(' = ')
			config[header][key] = value
			#print('    {0} = {1}'.format(key, value))

	return config


def write_ini_file(file_name, config):
	with open(file_name, 'wb') as f:
		for header, pairs in config.items():
			# Header
			f.write('[{0}]\r\n'.format(header))

			# Keys and values
			for key, value in pairs.items():
				f.write('{0} = {1}\r\n'.format(key, value))

			# Two spaces at the end of a section
			f.write('\r\n\r\n')

