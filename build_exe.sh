
rm -f server.exe
rm -f -R server/build
rm -f -R server/dist

cd server
python setup.py py2exe
cd ..
mv server/dist/server.exe server.exe

rm -f -R server/build
rm -f -R server/dist
