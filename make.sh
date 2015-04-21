
# Build the Dreamcast Identifier
cd server/identify_dreamcast_games
python setup.py py2exe
mv dist/identify_dreamcast_games.exe identify_dreamcast_games.exe
rm -rf dist
cd ../..

# Build the Playstation 2 Identifier
cd server/identify_playstation2_games
python setup.py py2exe
mv dist/identify_playstation2_games.exe identify_playstation2_games.exe
rm -rf dist
cd ../..

# Put everything inside the generated Go file
echo "Generating files"
go run server/generate/generate_included_files.go

# Build the Go exe
echo "Building emu_archive.exe"
go build server/emu_archive.go
mv emu_archive.exe emu_archive_$1.exe
emu_archive_$1.exe $1 local
