# emu_archive
HTML based front end for video game console emulators

After cloning the repository, remember to get the submodules too:

~~~bash
git submodule update --init --recursive
cd games
git checkout master
~~~

# Requirements

# python 2.7
http://www.python.org

# python modules

~~~bash
python -m pip install -U tornado
python -m pip install -U pypiwin32
~~~

# py2exe
http://www.py2exe.org

# Virtual Clone Drive
http://www.slysoft.com/en/virtual-clonedrive.html



# Build server exe

~~~bash
cd server
python setup.py py2exe
cd ..
rm -R server/build
mv server/dist/ server_exe/
~~~

# Run the server as an exe

~~~bash
server_exe/server.exe
~~~
http://localhost:9090

# Or run the server as python script

~~~bash
python server/server.py
~~~
http://localhost:9090
