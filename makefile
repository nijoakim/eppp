PREFIX=/usr/local/bin

interpreter:
	cd ../; python3

test:
	cd ../; python3 -m eppp.test

install:
	cd ../; eppp/setup.py build -b eppp/build install
	rm -rf build
	cp util.py $(PREFIX)/epppu
	cp epppu /etc/bash_completion.d/
