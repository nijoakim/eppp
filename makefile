# TODO: On compilation errors from .c files, rebuild next time 'make' is run

PREFIX=/usr/local/bin
INSTALL_EPPPU=1
INSTALL_EPPPU_COMPLETION=1
SOURCE=$(wildcard eppp/*.py) $(wildcard eppp/*/*.py) $(wildcard eppp/*.c) $(wildcard eppp/*/*.c)

.PHONY: all
all: build

.PHONY: clean
clean:
	rm -rf build
	rm -rf eppp/*.so

.PHONY: build
build: | build/

.PHONY: install
install: build
	./setup.py install
ifeq ($(INSTALL_EPPPU),1)
	cp eppp/util.py $(PREFIX)/epppu
ifeq ($(INSTALL_EPPPU_COMPLETION),1)
	cp bash_completion /etc/bash_completion.d/epppu
endif
endif

.PHONY: interpreter
interpreter: build
	python3 -i -c 'from eppp import *'

.PHONY: profile
profile: build
	python3 -m eppp.profiler

.PHONY:
test: build
	python3 -m eppp.tests.unit_test

.PHONY: benchmark
benchmark: build
	python3 -m eppp.tests.benchmark

build/: $(SOURCE)
	./setup.py build
	touch build
	cp build/*/eppp/*.so eppp/ 2>/dev/null || :

LOGFILE=eppp/tests/log/$(shell hostname)_$(shell date +%Y-%m-%d-%H:%M).log
log-benchmark:
	lscpu >> $(LOGFILE) 2>&1
	echo \\n--------\\n >> $(LOGFILE) 2>&1
	make benchmark >> $(LOGFILE) 2>&1
