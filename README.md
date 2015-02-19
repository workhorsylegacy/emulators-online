# emu_archive
HTML based front end for video game console emulators

After cloning the repository, remember to get the submodules too:

~~~bash
git clone http://github.com/workhorsy/emu_archive_meta_data games
~~~

# Requirements

# python 2.7
http://www.python.org

# python modules

~~~bash
python -m pip install -U tornado
python -m pip install -U pypiwin32
python -m pip install -U fuzzywuzzy
~~~

# py2exe
http://www.py2exe.org

# Virtual Clone Drive
http://www.slysoft.com/en/virtual-clonedrive.html



# Build server exe

~~~bash
./build_exe.sh
~~~

# Run the server as an exe

~~~bash
server.exe
~~~
http://localhost:9090

# Or run the server as python script

~~~bash
python server/server.py
~~~
http://localhost:9090
