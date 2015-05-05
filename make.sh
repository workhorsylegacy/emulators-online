
# If there are no arguments, print the correct usage and exit
if [ "$#" -ne 1 ]; then
	echo "Build and run emulators_online.exe" >&2
	echo "Usage: make.sh port" >&2
	echo "Example: make.sh 9090" >&2
	exit 1
fi

rm -f emulators_online_$1.exe

# Build the Dreamcast Identifier
cd client/identify_dreamcast_games
python setup.py py2exe
mv dist/identify_dreamcast_games.exe identify_dreamcast_games.exe
rm -rf dist
cd ../..

# Build the Playstation 2 Identifier
cd client/identify_playstation2_games
python setup.py py2exe
mv dist/identify_playstation2_games.exe identify_playstation2_games.exe
rm -rf dist
cd ../..

# Put everything inside the generated Go file
echo "Generating files"
go run client/generate/generate_included_files.go

# Build the Go exe
echo "Building emulators_online.exe"
go build client/emulators_online.go
mv emulators_online.exe emulators_online_$1.exe
emulators_online_$1.exe $1 local
