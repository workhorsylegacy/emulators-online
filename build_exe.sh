
cd server
python setup.py py2exe
cd ..
rm -f -R server/build
rm -f -R server/dist
mv server/dist/server.exe server.exe
rm -f -R server/build
rm -f -R server/dist
