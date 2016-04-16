test:
	cd ../; python3 -m eppp.test

install:
	cd ../; eppp/setup.py build -b eppp/build install
	rm -rf build
