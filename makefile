PREFIX=/usr/local/bin
INSTALL_EPPPU=1
INSTALL_EPPPU_COMPLETION=1

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
ifeq ($(INSTALL_EPPPU),1)
	cp util.py $(PREFIX)/epppu
ifeq ($(INSTALL_EPPPU_COMPLETION),1)
	cp epppu /etc/bash_completion.d/
endif
endif
