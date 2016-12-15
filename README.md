# EPPP - Electronics Post-simulation Python Package (E triple-P)

EPPP is a Python 3 package for processing and analysing electronic simulation data.

It is very much work in progress and the documentation is currently lacking in many areas. Also, in this early stage of development, everything is subject to change. It is even somewhat likely that some of the current functionality will be stripped away or moved to another project.

EPPP comes as a python module but also defines a program, `epppu`, "EPPP utilities", that uses the module to provide a convenient command-line interface to some of the EPPP functionality. For example:

	$ epppu network 88120
	(220.0 k || (47.00 k + 100.0 k)) = 88.12 k

uses EPPPs impedance network calculator to generate an E6 resistor network with an equivalent resistance of 88.123 kΩ.

The library provides, among many other things, functions for plotting Bode diagrams and extracting break frequencies from frequency response data.

## Library
TODO: Expand this section when it is more clear what does what

- error.py
- inout.py
- log.py
- plot.py
- calc/lumped\_network.py
- calc/misc.py

## EPPP utilities
`epppu` currently provides the following functions:

- `epppu network`
- `epppu parallel`

For doumentation on the different commands use
`epppu <command> -h`.

## Installing

### Dependencies
- python3
- python3-numpy
- python3-scipy
- python3-matplotlib

On Debian-based systems,

	$ sudo aptitude install python3 python3-numpy python3-scipy python3-matplotlib

should install all the dependencies.

### Installing EPPP
To install run:

	$ sudo make install

To change the install prefix add `PREFIX=<prefix>`. If you don't want to install the EPPP utilities, add `INSTALL_EPPPU=0` and if you don't want bash completion for the EPPP utilities, add `INSTALL_EPPPU_COMPLETION=0`.

## Development

The logging verbosity can be set with the function `eppp.set_log_level()`.

To run unit and performance tests, run:

	$ make test

For code profiling, run:

	$ make profile