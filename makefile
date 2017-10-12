# TODO: Don't fail to build if 'libpython3-dev is missing'

PREFIX=/usr/local/bin
INSTALL_EPPPU=1
INSTALL_EPPPU_COMPLETION=1
SOURCE=$(wildcard eppp/*.py) $(wildcard eppp/*/*.py) $(wildcard eppp/*.c) $(wildcard eppp/*/*.c)

all: unit-test benchmark

clean:
	rm -rf build
	rm -rf eppp/*.so

build: $(SOURCE)
	./setup.py build
	touch build
	cp build/*/eppp/*.so eppp/

interpreter: build
	python3

profile: build
	python3 -m eppp.profiler

unit-test: build
	python3 -m eppp.tests.unit_test

benchmark: build
	python3 -m eppp.tests.benchmark

LOGFILE=eppp/tests/log/$(shell hostname)_$(shell date +%Y-%m-%d-%H:%M).log
log-benchmark:
	lscpu >> $(LOGFILE) 2>&1
	echo \\n--------\\n >> $(LOGFILE) 2>&1
	make benchmark >> $(LOGFILE) 2>&1

install: build
	./setup.py install
ifeq ($(INSTALL_EPPPU),1)
	cp eppp/util.py $(PREFIX)/epppu
ifeq ($(INSTALL_EPPPU_COMPLETION),1)
	cp bash_completion /etc/bash_completion.d/epppu
endif
endif
