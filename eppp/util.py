#!/usr/bin/env python3

# Copyright 2014-2020 Joakim Nilsson
#
# This file is part of EPPP.
#
# EPPP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EPPP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EPPP.  If not, see <http://www.gnu.org/licenses/>.

# TODO: Possibility to read from stdin. (Switch for this?)
# TODO: Repeated arguments for some commands should repeat the operation.
# TODO: Possibility to omit unit.

#=========
# Imports
#=========

# External
import argparse as ap
import re
import sys
import operator as op
from math import inf

# Internal
import eppp
import eppp.calc

#========
# Parser
#========

# Availible sub-commands
CMDS = [
	'expression',
	'make-resistance',
	'parallel',
	'reactance',
	'susceptance',
	'voltage-division',
	'current-division',
	'skin-depth',
]

# Description
desc_str = 'Executes a command based on the functionality provided by the EPPP library. Available commands are: %s.' % ', '.join(map(lambda x: "'"+ x +"'", CMDS))

# Expand metric prefixes from 'argv'
PREFIXES = {
	'y': 1e-24,
	'z': 1e-21,
	'a': 1e-18,
	'f': 1e-15,
	'p': 1e-12,
	'n': 1e-9,
	'µ': 1e-6,
	'u': 1e-6,
	'm': 1e-3,
	'k': 1e3,
	'M': 1e6,
	'G': 1e9,
	'T': 1e12,
	'P': 1e15,
	'E': 1e18,
	'Z': 1e21,
	'Y': 1e24,
}
for i, arg in enumerate(sys.argv):
	# Skip script and command names
	if i > 1:
		# String to match on
		match_str = ''
		match_str += r'(([1-9][0-9]*\.?[0-9]*)|(\.[0-9]+))([Ee][+-]?[0-9]+)?' # Floating point number
		match_str += '['+ '|'.join(PREFIXES.keys()) +']'                      # Metric prefix
		print(match_str)

		# Substitute numbers with metric prefixes with pure floats
		# TODO: Bug: '1||1' gives error; '1 || 1' does not
		# TODO: Use assignment expression in while loop when Python 3.8 becomes standard
		while re.search(match_str, arg):
			match      = re.search(match_str, arg)
			num        = float(arg[match.start() : match.end()-1]) # Parse into float
			multiplier = PREFIXES[arg[match.end()-1]]              # Look up prefix

			# Expand argument
			arg = \
				arg[:match.start()] + \
				str(num*multiplier) + \
				arg[match.end():]
		sys.argv[i] = arg

# Parse global arguments
parser = ap.ArgumentParser(description=desc_str)
parser.add_argument('command')
parser.add_argument(
	'-sf',
	'--significant-figures',
	type=int,
	default = 4,
	nargs   = '?',
	help    = 'Number of significant figures to print with. (default: %(default)s)',
)
parser.add_argument(
	'-ns',
	'--notation-style',
	type=str,
	default = 'metric',
	nargs   = '?',
	help    = 'Style used for numbers that are printed. (metric, engineering or scientific) (default: %(default)s)',
)
parser.add_argument('command-arguments', nargs=ap.REMAINDER)
global_args = parser.parse_args()

# Set default significant figures
eppp.set_default_str_sci_args(
	num_sig_figs   = global_args.significant_figures,
	notation_style = global_args.notation_style,
)

# Match input command with available command
cmd_in = global_args.command
pred = re.compile(cmd_in +'.*')
matches = []
for matchcmd in CMDS:
	if pred.match(matchcmd) is not None:
		matches.append(matchcmd)
		cmd = matchcmd
num_matches = len(matches)

# Check for mismatches and ambiguities
if num_matches == 0:
	sys.stderr.write("'%s' does not match any command.\n" % cmd_in)
	exit(1)
elif num_matches == 2:
	cmds_str = make_cmds_str(matches)
	sys.stderr.write('%s is ambiguous.\n\nDid you mean any of these commands?\n%s\n' % (cmd_in, cmds_str))
	exit(1)

# Remove global arguments for argv
sys.argv = [sys.argv[0]] + vars(global_args)['command-arguments']

#======================
# 'expression' command
#======================

if cmd == 'expression':
	# Parse
	parser = ap.ArgumentParser(
		description = "Evaluates an expression. Electronic operators, such as the parallel operator, '||' are supported.",
	)
	parser.add_argument(
		'expression',
		type  = str,
		nargs = '+',
		help  = "Expression. Valid operators are: '||' or '//', '+', '-', '*', '/' and '^'.",
	)
	args = parser.parse_args()

	# Make string from arguments
	expr_str = ' '.join(args.expression)

	# Print the result
	eppp.inout.print_sci(eppp.calc.electronic_eval(expr_str))

#==========================
# 'make-resistance' command
#==========================
# TODO: Add frequency and support for inductors and capacitors?
# TODO: Switches for what to print

if cmd == 'make-resistance':
	# Parse
	parser = ap.ArgumentParser(
		description = 'Finds a network of passive components matching a specified (possibly complex) value.'
	)
	parser.add_argument(
		'target',
		type = float, # TODO: Change to complex when supported
		help = 'Target resistance.',
	)
	parser.add_argument(
		'-t',
		'--tolerance',
		type    = float,
		nargs   = '?',
		default = 0.01,
		help    = 'Maximum relative error for the resulting network. (default: %(default)s)',
	)
	parser.add_argument(
		'-n',
		'--num_components',
		type    = int,
		nargs   = '?',
		default = -1,
		help    = 'Maximum number of components for the resulting network. Negative values yield no limit. (default: -1)',
	)
	parser.add_argument(
		'-s',
		'--series',
		type    = str,
		default = 'E6',
		help    = 'E-series from which to get available components. (E3, E6, E12, E24, E48, E96 or E192) (default: %(default)s)',
	)
	parser.add_argument(
		'-mr',
		'--min-resistance',
		type    = float,
		default = 10,
		help    = 'Minimum resistance used when generating the series (default: %(default)s)',
	)
	parser.add_argument(
		'-Mr',
		'--max-resistance',
		type    = float,
		default = 10e6,
		help    = 'Maximum resistance used when generating the series (default: %(default)s)',
	)
	parser.add_argument(
		'--configuration',
		type    = str,
		default = 'any',
		help    = 'Valid configurations in the resulting network. (series, parallel or any) (default: %(default)s)',
	)
	parser.add_argument(
		'-pe',
		'--print-error',
		action = 'store_true',
		help   = 'Prints the relative error by which the resulting network deviates from the target.',
	)
	parser.add_argument(
		'-or',
		'--omit-result',
		action = 'store_false',
		help   = 'Omits printing the value of the network',
	)
	args = parser.parse_args()

	# Generate list of operations
	if args.configuration == 'any':
		ops = [eppp.calc.parallel_impedance, op.add]
	elif args.configuration == 'series':
		ops = [op.add]
	elif args.configuration == 'parallel':
		ops = [eppp.calc.parallel_impedance]
	else:
		pass
		# TODO: Error

	# Get the expression
	expr = eppp.calc.make_resistance(
		args.target,
		avail_vals    = eppp.calc.get_avail_vals(args.series, min_val=args.min_resistance, max_val=args.max_resistance),
		tolerance     = args.tolerance,
		max_num_comps = args.num_components,
		avail_ops     = ops,
	)
	res = expr.evaluate()

	# Print error
	print(str(expr) + (' = '+ eppp.str_sci(res) if args.omit_result else ''))
	if args.print_error:
		eppp.print_sci(
			(res - args.target) / args.target,
			quantity = 'relative error',
		)

#====================
# 'parallel' command
#====================

if cmd == 'parallel':
	# Parse
	parser = ap.ArgumentParser(
		description = 'Calculates the equivalent impedance of a set of parallel connected components.'
	)
	parser.add_argument(
		'values',
		type  = complex,
		nargs = '+',
		help = 'List of parallel impedances.'
	)
	vals = parser.parse_args().values

	# Do the calculation
	res = eppp.calc.parallel_impedance(*vals)

	# Print the result
	eppp.print_sci(res, unit='Ω')

#=====================
# 'reactance' command
#=====================

if cmd == 'reactance':
	# Parse
	parser = ap.ArgumentParser(
		description = '', # TODO
	)
	parser.add_argument(
		'type',
		type = str,
		help = "Type of component. ('inductor or capacitor')",
	)
	parser.add_argument(
		'value',
		type = float,
		help = 'Component value. (Henry or Farad)',
	)
	parser.add_argument(
		'frequency',
		type = float,
		help = 'Frequency. (Hertz)',
	)
	args = parser.parse_args()

	# Determine type of reactive component
	if args.type == 'inductor'[:len(args.type)]:
		res = eppp.calc.inductor_impedance(args.value, args.frequency)
	elif args.type == 'capacitor'[:len(args.type)]:
		res = eppp.calc.capacitor_impedance(args.value, args.frequency)
	else:
		raise ValueError("Argument 2 must be either 'inductor' or 'capacitor'.")

	# Print the result
	eppp.print_sci(res.imag, unit='Ω')

#=======================
# 'susceptance' command
#=======================

if cmd == 'susceptance':
	# Parse
	parser = ap.ArgumentParser(
		description = '', # TODO
	)
	parser.add_argument(
		'type',
		type = str,
		help = "Type of component. ('inductor or capacitor')",
	)
	parser.add_argument(
		'value',
		type = float,
		help = 'Component value. (Henry or Farad)',
	)
	parser.add_argument(
		'frequency',
		type = float,
		help = 'Frequency. (Hertz)',
	)
	args = parser.parse_args()

	# Determine type of reactive component
	if args.type == 'inductor'[:len(args.type)]:
		res = eppp.calc.inductor_admittance(args.value, args.frequency)
	elif args.type == 'capacitor'[:len(args.type)]:
		res = eppp.calc.capacitor_admittance(args.value, args.frequency)
	else:
		raise ValueError("Argument 2 must be either 'inductor' or 'capacitor'.")

	# Print the result
	eppp.print_sci(res.imag, unit='S')

#============================
# 'voltage-division' command
#============================

if cmd == 'voltage-division':
	# Parse
	parser = ap.ArgumentParser(
		description = 'Calculates the voltage divided over series-connected impedances.'
	)
	parser.add_argument(
		'voltage',
		type = complex,
		help = 'Source voltage.',
	)
	parser.add_argument(
		'main_impedance',
		type = complex,
		help = 'Main impedance.',
	)
	parser.add_argument(
		'impedances',
		type  = complex,
		nargs = '*',
		help = 'List of other series-connected impedances.'
	)
	args = parser.parse_args()
	main_imp = parser.parse_args().main_impedance
	imps     = parser.parse_args().impedances

	# Do the calculation
	res_voltage = eppp.calc.voltage_division(
		args.voltage,
		args.main_impedance,
		*args.impedances,
	)

	# Print the result
	eppp.print_sci(res_voltage, unit='V')

#============================
# 'current-division' command
#============================

if cmd == 'current-division':
	# Parse
	parser = ap.ArgumentParser(
		description = 'Calculates the current divided between parallel-connected impedances.'
	)
	parser.add_argument(
		'current',
		type = complex,
		help = 'Source current.',
	)
	parser.add_argument(
		'main_impedance',
		type = complex,
		help = 'Main impedance.',
	)
	parser.add_argument(
		'impedances',
		type  = complex,
		nargs = '*',
		help = 'List of other parallel-connected impedances.'
	)
	args = parser.parse_args()

	# Do the calculation
	current = eppp.calc.current_division(
		args.current,
		args.main_impedance,
		*args.impedances,
	)

	# Print the result
	eppp.print_sci(current, unit='A')

#======================
# 'skin-depth' command
#======================

if cmd == 'skin-depth':
	# Parse
	parser = ap.ArgumentParser(
		description = 'Calculates the skin depth.'
	)
	parser.add_argument(
		'resistivity',
		type = float,
		help = 'Resistivity of the conductor. [Ω/m]',
	)
	parser.add_argument(
		'frequency',
		type = float,
		help = 'Frequency [Hz].',
	)
	parser.add_argument(
		'-rpi',
		'--relative-permittivity',
		type    = float,
		default = 1,
		nargs   = '?',
		help    = 'Relative permittivity of the conductor.'
	)
	parser.add_argument(
		'-rpe',
		'--relative-permeability',
		type    = float,
		default = 1,
		nargs   = '?',
		help    = 'Relative permeability of the conductor.'
	)
	args = parser.parse_args()

	# Do the calculation
	depth = eppp.calc.skin_depth(
		args.resistivity,
		args.frequency,
		rel_permittivity = args.relative_permittivity,
		rel_permeability = args.relative_permeability,
	)

	# Print the result
	eppp.print_sci(depth, unit='m')
