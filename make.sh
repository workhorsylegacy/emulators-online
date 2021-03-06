# Copyright (c) 2015, Matthew Brennan Jones <matthew.brennan.jones@gmail.com>
# emulators-online is a HTML based front end for video game console emulators
# It uses the GNU AGPL 3 license
# It is hosted at: https://github.com/workhorsylegacy/emulators-online

#set -e

function build {
	# Get the location of Bash and a temp file
	bash=`cmd //c "echo %ProgramFiles%\\Git\\git-bash.exe"`
	temp_file=`cmd //c "echo %TEMP%\\bash_path"`
	bash=`sed 's,\\\\,/,g' <<< $bash`
	temp_file=`sed 's,\\\\,/,g' <<< $temp_file`
	rm -f $temp_file

	# Get a fresh copy of the PATH
	echo "Updating PATH ..."
	out=$(schtasks //delete //f //tn "Build" 2>&1)
	out=$(schtasks //create //f //tn "Build" //sc once //st 23:59 //tr "'$bash' -c 'echo \$PATH > $temp_file'" 2>&1)
	out=$(schtasks //run //tn "Build" 2>&1)
	while [ ! -f $temp_file ]; do sleep 0.3; done
	PATH=`cat "$temp_file"`
	rm -f $temp_file

	# Get a fresh copy of the GOPATH
	echo "Updating GOPATH ..."
	out=$(schtasks //delete //f //tn "Build" 2>&1)
	out=$(schtasks //create //f //tn "Build" //sc once //st 23:59 //tr "'$bash' -c 'echo \$GOPATH > $temp_file'" 2>&1)
	out=$(schtasks //run //tn "Build" 2>&1)
	while [ ! -f $temp_file ]; do sleep 0.3; done
	GOPATH=`cat "$temp_file"`
	rm -f $temp_file

	out=$(schtasks //delete //f //tn "Build")

	echo "Checking for system requirements ..."

	# Make sure python is installed
	PYTHON=""
	if ! type python >/dev/null 2>&1; then
		if ! type py >/dev/null 2>&1; then
			echo "Python was not found. Please install a 32 bit Python 3." >&2
			return
		else
			PYTHON="py"
		fi
	else
		PYTHON="python"
	fi

	# Make sure python is 32 bit
	python_bits=$($PYTHON -c 'import struct;print(struct.calcsize("P") * 8)')
	if [ $python_bits -ne 32 ]; then
		echo "Python was found, but it is not 32 bit! Please install a 32 bit Python 3."
		return
	fi

	# Make sure python is 3.X
	python_version=$($PYTHON -c 'import sys;print(sys.version_info[0])')
	if [ $python_version -ne 3 ]; then
		echo "Python was found, but it is not version 3.X! Please install a 32 bit Python 3."
		return
	fi

	# Make sure the Python module pyreadline is installed
	if ! $($PYTHON -c "import pyreadline" &> /dev/null); then
		echo "Python module pyreadline was not found. Please install." >&2
		return
	fi

	# Make sure the Python module py2exe is installed
	if ! $($PYTHON -c "import py2exe" &> /dev/null); then
		echo "Python module py2exe was not found. Please install." >&2
		return
	fi

	# Make sure GCC is installed
	if ! type gcc >/dev/null 2>&1; then
		echo "GCC was not found. Please install MinGW." >&2
		return
	fi

	# Make sure Go is installed
	if ! type go >/dev/null 2>&1; then
		echo "Go was not found. Please install 32 bit Go." >&2
		return
	fi

	# Make sure Go is 32 bit
	if [ $(go env GOARCH) -ne 386 ]; then
		echo "Go was found, but it is not 32 bit! Please install 32 bit Go."
		return
	fi

	# Make sure GOPATH is set
	if [ -z "$GOPATH" ]; then
		echo "Go environmental variable GOPATH is not set. Please set GOPATH to workspace location."
		return
	fi

	# Make sure Go packages are installed
	if ! $(go list 'golang.org/x/net/websocket' &> /dev/null); then
		echo "Go package 'golang.org/x/net/websocket' is not installed. Please install it."
		return
	fi

	# Remove the exes
	rm -f emulators_online_client.exe
	rm -f client/identify_games/identify_games.exe

	# Build the game Identifier
	cd client/identify_games
	$PYTHON setup.py py2exe
	mv dist/identify_games.exe identify_games.exe
	rm -rf dist
	cd ../..

	# Put everything inside the generated Go file
	echo "Generating files ..."
	go run client/generate/generate_included_files.go

	# Build the client exe
	echo "Building emulators_online_client.exe ..."
	go build client/emulators_online_client.go

	# Run the client
	./emulators_online_client.exe $1 local
}

# If there are no arguments, print the correct usage
if [ "$#" -ne 1 ]; then
	echo "Build and run emulators_online_client.exe" >&2
	echo "Usage: ./make.sh port" >&2
	echo "Example: ./make.sh 9090" >&2
# Or build the software
else
	build $@
fi
