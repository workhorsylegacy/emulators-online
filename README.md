# emulators-online
HTML based front end for video game console emulators

It uses WebSockets to connect the HTML front-end, to a Go back-end. The 
back-end manages the emulators and game files. The project was written in 
Python, but is slowly being converted to Go. For now, Python is required to 
to build the Go exe, but is not required at runtime.


Install python 3.X
-----
http://www.python.org
~~~bash
python -m pip install -U py2exe
python -m pip install -U pyreadline
~~~

Install 32 bit MinGW
-----
http://sourceforge.net/projects/mingw/?source=typ_redirect
Install base and gcc-c++ packages

Install 32 bit Go
-----
https://storage.googleapis.com/golang/go1.4.2.windows-386.msi

Set GOPATH environmental variable
-----
C:/WORKSPACE_GO/

Install WebSockets Module
-----
~~~bash
go get golang.org/x/net/websocket
~~~

Checkout the code
-----
~~~bash
cd C:/WORKSPACE_GO/src
git clone http://github.com/workhorsy/emulators-online
cd emulators-online
git clone http://github.com/workhorsy/emu_archive_meta_data games
~~~


Build and run the exe
-----
~~~bash
cd C:/WORKSPACE_GO/src/emulators-online
make.sh 9090
~~~

Visit this url
~~~bash
http://localhost:9090
~~~
