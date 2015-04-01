# emu_archive
HTML based front end for video game console emulators

After cloning the repository, remember to get the submodules too:


Install 32bit MinGW
-----
http://sourceforge.net/projects/mingw/?source=typ_redirect
Install base and gcc-c++ packages

Install 32 bit Go
-----
https://storage.googleapis.com/golang/go1.4.2.windows-386.msi

Set GOPATH to
-----
C:\GO_WORKSPACE\

Install WebSockets Module
-----
go get golang.org/x/net/websocket

Install python 3.X
-----
http://www.python.org

Install Virtual Clone Drive
-----
http://www.slysoft.com/en/virtual-clonedrive.html


# Checkout the code

~~~bash
cd C:\GO_WORKSPACE\src
git clone http://github.com/workhorsy/emu_archive
cd emu_archive
git clone http://github.com/workhorsy/emu_archive_meta_data games
~~~


# Build server exe

~~~bash
cd C:\GO_WORKSPACE\src\emu_archive
go run server/server.go
~~~

Visit this url
http://localhost:9090

