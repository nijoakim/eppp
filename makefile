PREFIX=/usr/local/bin
INSTALL_EPPPU=1
INSTALL_EPPPU_COMPLETION=1

all: unit-test benchmark

interpreter:
	cd ../; python3

profile:
	cd ../; python3 -m eppp.profiler

unit-test:
	cd ../; python3 -m eppp.tests.unit_test

benchmark:
	cd ../; python3 -m eppp.tests.benchmark

LOGFILE=tests/log/$(shell hostname)_$(shell date +%Y-%m-%d-%H:%M).log
log-benchmark:
	lscpu >> $(LOGFILE) 2>&1
	echo \\n--------\\n >> $(LOGFILE) 2>&1
	make benchmark >> $(LOGFILE) 2>&1

install:
	cd ../; eppp/setup.py build -b eppp/build install
	rm -rf build
ifeq ($(INSTALL_EPPPU),1)
	cp util.py $(PREFIX)/epppu
ifeq ($(INSTALL_EPPPU_COMPLETION),1)
	cp bash_completion /etc/bash_completion.d/epppu
endif
endif
