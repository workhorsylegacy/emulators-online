

# If there are no arguments, print the correct usage and exit
if [ "$#" -ne 1 ]; then
	echo "Build and run emulators_online_client.exe" >&2
	echo "Usage: make.sh port" >&2
	echo "Example: make.sh 9090" >&2
	exit 1
fi

# Get a fresh copy of the PATH.
# Have it copied from a new Bash session to a temp file
echo "Updating PATH ..."
bash=`cmd //c "echo %ProgramFiles%\\Git\\git-bash.exe"`
bash_path=`cmd //c "echo %TEMP%\\bash_path"`
bash=`sed 's,\\\\,/,g' <<< $bash`
bash_path=`sed 's,\\\\,/,g' <<< $bash_path`
./get_bash_path.bat "$bash" "$bash_path" &> /dev/null
sleep 3 # FIXME: Having to wait for the schtasks sucks
PATH=`cat $bash_path`

echo "Checking for system requirements ..."

# Make sure python is installed
if ! type python >/dev/null 2>&1; then
	echo "Python was not found. Please install a 32 bit Python 3." >&2
	exit 1
fi

# Make sure python is 32 bit
python_bits=$(python -c 'import struct;print(struct.calcsize("P") * 8)')
if [ $python_bits -ne 32 ]; then
	echo "Python was found, but it is not 32 bit! Please install a 32 bit Python 3."
	exit 1
fi

# Make sure python is 3.X
python_version=$(python -c 'import sys;print(sys.version_info[0])')
if [ $python_version -ne 3 ]; then
	echo "Python was found, but it is not version 3.X! Please install a 32 bit Python 3."
	exit 1
fi

# Make sure the Python module pyreadline is installed
if ! $(python -c "import pyreadline" &> /dev/null); then
	echo "Python module pyreadline was not found. Please install." >&2
	exit 1
fi

# Make sure the Python module py2exe is installed
if ! $(python -c "import py2exe" &> /dev/null); then
	echo "Python module py2exe was not found. Please install." >&2
	exit 1
fi

# Make sure Go is installed
if ! type go >/dev/null 2>&1; then
	echo "Go was not found. Please install 32 bit Go." >&2
	exit 1
fi

# Make sure Go is 32 bit
go_arch=$(go env GOARCH)
if [ $go_arch -ne 386 ]; then
	echo "Go was found, but it is not 32 bit! Please install 32 bit Go."
	exit 1
fi

# Make sure GOPATH is set
if [ -z "$GOPATH" ]; then
	echo "Go environmental variable GOPATH is not set. Please set GOPATH to workspace location."
	exit 1
fi

# Make sure Go packages are installed
if ! $(go list 'golang.org/x/net/websocket' &> /dev/null); then
	echo "Go package 'golang.org/x/net/websocket' is not installed. Please install it."
	exit 1
fi

# Make sure GCC is installed
if ! type gcc >/dev/null 2>&1; then
	echo "GCC was not found. Please install MinGW." >&2
	exit 1
fi

# Remove the exes
rm -f emulators_online_client.exe
rm -f client/identify_games/identify_games.exe

# Build the game Identifier
cd client/identify_games
python setup.py py2exe
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
