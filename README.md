# emu_archive
HTML based front end for video game console emulators

After cloning the repository, remember to get the submodules too:


Install python 3.X
-----
http://www.python.org

Install 32 bit MinGW
-----
http://sourceforge.net/projects/mingw/?source=typ_redirect
Install base and gcc-c++ packages

Install 32 bit Go
-----
https://storage.googleapis.com/golang/go1.4.2.windows-386.msi

Set GOPATH environmental variable to
-----
C:/GO_WORKSPACE/

Install WebSockets Module
-----
~~~bash
go get golang.org/x/net/websocket
~~~

Checkout the code
-----
~~~bash
cd C:/GO_WORKSPACE/src
git clone http://github.com/workhorsy/emu_archive
cd emu_archive
git clone http://github.com/workhorsy/emu_archive_meta_data games
~~~


Build and run the exe
-----
~~~bash
cd C:/GO_WORKSPACE/src/emu_archive
go run server/server.go
~~~

Visit this url
http://localhost:9090

