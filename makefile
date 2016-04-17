# TODO Possiblity to switch off installing epppu and bash completions

PREFIX=/usr/local/bin

all: test

interpreter:
	cd ../; python3

profile:
	cd ../; python3 -m eppp.profiler

test:
	cd ../; python3 -m eppp.test

install:
	cd ../; eppp/setup.py build -b eppp/build install
	rm -rf build
	cp util.py $(PREFIX)/epppu
	cp epppu /etc/bash_completion.d/
