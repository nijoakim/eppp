# EPPP - Electronics Post-simulation Python Package (E triple-P)

EPPP is a Python package for processing and analysing electronic simulation data.

It is very much work in progress and the documentation is currently lacking in many areas. Also, in this early stage of development, everything is subject to change. It is even somewhat likely that some of the current functionality will be stripped away or moved to another project.

EPPP comes as a python module but also defines a program, `epppu`, "EPPP utilities", that uses the module to provide a convenient command-line interface to some of the EPPP functionality. For example:

	$ epppu network 88120
	(220.0 k || (47.00 k + 100.0 k)) = 88.12 k

uses EPPPs impedance network calculator to generate an E6 resistor network with an equivalent resistance of 88.12 kΩ, while

	$ epppu expression '10e3 // (47 + 2200)'
	1.835 k

evaluates an expression which includes the parallel impedance operator, '//'. (The quotes in the example are used to avoid having to escape the parentheses. `$ epppu expression 10e3 // \(47 + 2200\)` would have been equally valid.)

The library provides, among many other things, functions for plotting Bode diagrams and extracting break frequencies from frequency response data.

## Library
Structure of sub-modules:
- `eppp.calc`: Mathematical operations and calculations as well as electronic circuit generation.
- `eppp.inout`: Reading input data and pretty printing.
- `eppp.log`: Control of the logging verbosity.
- `eppp.plot`: Generation of various plots using `matplotlib`. For example `eppp.plot.bode` generates a Bode plot.

Everything provided by the sub-modules are also imported into the root module.

## EPPP utilities
`epppu` currently provides the following commands:

- `epppu expression`
- `epppu impedance`
- `epppu network`
- `epppu parallel`

For doumentation on the different commands use
`epppu <command> -h`.

## Installation

### Dependencies
- python3
- python3-distutils
- python3-numpy
- python3-scipy
- python3-matplotlib (optional: required by `eppp.plot`)
- python3-dev (optional: performance boost for some functions through C bindings)

On Debian-based systems,

	$ sudo aptitude install python3 python3-numpy python3-matplotlib libpython3-dev

should install all the dependencies.

### Installing EPPP
To install run:

	$ sudo make install

To change the install prefix add `PREFIX=<prefix>`. If you don't want to install the EPPP utilities, add `INSTALL_EPPPU=0` and if you don't want bash completion for the EPPP utilities, add `INSTALL_EPPPU_COMPLETION=0`.

## Development

The logging verbosity can be set with the function `eppp.log.set_log_level()`.

To run unit and performance tests, run:

	$ make unit-test

For code profiling, run:

	$ make profile

For benchmarking, run:

	$ make benchmark
