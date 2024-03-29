#!/usr/bin/env python3

# Copyright 2014-2023 Joakim Nilsson
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
# TODO: Usage string omits sub-command.

#=========
# Imports
#=========

# External
import argparse as ap
import operator as op
import os
import re
import readline
import sys
import traceback
from math import inf

# Internal
import eppp

#===========
# Functions
#===========

def make_cmds_str(cmds):
	return ', '.join(map(lambda x: "'"+ x +"'", cmds))

def expand_metric_prefixes(string):
	# String to match on
	match_str = ''
	match_str += r'(^|\W|_)'                                           # Start of line, non-alphanumeric or underscore
	match_str += r'(([0-9]+\.?[0-9]*)|(\.[0-9]+))([Ee][+-]?[0-9]+)?j?' # Real or imaginary number
	match_str += r'\s*'                                                # Optional whitespace
	match_str += '['+ ''.join(PREFIXES.keys()) +']'                    # Metric prefixes

	# Substitute numbers with metric prefixes with pure floats
	while (match := re.search(match_str, string)):
		# Match number
		start = match.start()
		end   = match.end()

		# Advance start index if not right at number
		if  not '0' <= string[start] <= '9' \
		and not string[start] == '.':
			start += 1

		# Parse
		num        = complex(string[start : end-1]) # Parse complex
		multiplier = PREFIXES[string[end-1]]        # Parse prefix

		# Convert to float if imaginary part is zero
		if num.imag == 0:
			num = num.real

		# Expand string
		string = \
			string[:start] + \
			str(num*multiplier) +' '+ \
			string[end:]
	return string

#========
# Parser
#========

# Availible sub-commands
# Indentation denotes grouping of related commands while maintaining approximate alphabetical sorting
CMDS = [
	'from-db',
		'to-db',
	'expression',
	'make-resistance',
	'parallel',
	'reactance',
	'susceptance',
	'voltage-division',
		'current-division',
	'skin-depth',
	'wavelength',
	'wire-resistance',
		'plates-capacitance',
]

# Description
desc_str = 'Executes a command based on the functionality provided by the EPPP library. Available commands are: %s.' % make_cmds_str(CMDS)

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
	if i > 1: # Skip script and command names
		sys.argv[i] = expand_metric_prefixes(arg)

# Parse global arguments
parser = ap.ArgumentParser(description=desc_str)
parser.add_argument('command')
parser.add_argument(
	'-sf',
	'--significant-figures',
	type    = int,
	default = 4,
	nargs   = '?',
	help    = 'Number of significant figures to print with. (default: %(default)s)',
)
parser.add_argument(
	'-ns',
	'--notation-style',
	type    = str,
	default = 'metric',
	nargs   = '?',
	help    = 'Style used for numbers that are printed. (metric, engineering or scientific) (default: %(default)s)',
)
parser.add_argument(
	'-pf',
	'--polar-form',
	action  = 'store_true',
	help    = 'TODO',
)
parser.add_argument(
	'-au',
	'--angle-unit',
	type    = str,
	default = '',
	nargs   = '?',
	help    = 'TODO',
)
parser.add_argument('command-arguments', nargs=ap.REMAINDER)
global_args = parser.parse_args()

# Set default significant figures
eppp.set_default_str_sci_args(
	num_sig_figs   = global_args.significant_figures,
	notation_style = global_args.notation_style,
	polar_form     = global_args.polar_form,
	angle_unit     = global_args.angle_unit,
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

#===================
# 'from-db' command
#===================

if cmd == 'from-db':
	parser = ap.ArgumentParser(
		description = "Converts a number from its decibel form.",
	)

	parser.add_argument(
		"x",
		type = float,
		help = "Decibel value to convert from.",
	)

	parser.add_argument(
		'type',
		type = str,
		help  = "Whether to use the power decibel or amplitude decibel definition. Valid values are 'power' and 'amplitude'."
	)

	args = parser.parse_args()

	# Print the result
	eppp.inout.print_sci(eppp.from_db(args.x, args.type))

#=================
# 'to-db' command
#=================

if cmd == 'to-db':
	parser = ap.ArgumentParser(
		description = "Converts a number to its decibel form.",
	)

	parser.add_argument(
		"x",
		type = float,
		help = "Number to be converted.",
	)

	parser.add_argument(
		'type',
		type = str,
		help  = "Whether to use the power decibel or amplitude decibel definition. Valid values are 'power' and 'amplitude'."
	)

	args = parser.parse_args()

	# Print the result
	eppp.inout.print_sci(eppp.to_db(args.x, args.type), 'dB')

#======================
# 'expression' command
#======================

if cmd == 'expression':
	parser = ap.ArgumentParser(
		description = "Evaluates an expression. In addition to the normal arithmetic operators, addition ('+'), subtraction ('-'), multiplication ('*'), division ('/'), exponentiation ('^' or '**') and assignment ('='), the parallel operator, '||' or '//', is supported. Functions defined in numpy as well as constants defined in scipy.constants are also supported. Superscript digits are expanded, which means that 2³ would expand to 2**(3). The result of the evaluation is assigned to the variable 'ans'.",
	)

	parser.add_argument(
		'-i',
		'--interactive',
		action = 'store_true',
		help   = 'Runs command in interactive mode.',
	)

	parser.add_argument(
		'-p',
		'--plain',
		action = 'store_true',
		help   = 'In interactive mode, do not modify the font.',
	)

	parser.add_argument(
		'expression',
		type  = str,
		nargs = '*', # TODO: '+' if -i is given?
		help  = "Expression to evaluate. Valid operators are: '=', '||' or '//', '+', '-', '*', '/' and '^' or '**'."
	)

	args = parser.parse_args()

	# Interactive mode
	if args.interactive:
		# Print intro message
		print(f'EPPP utilities expression interpreter version {eppp.__version__}. Press CTRL+D to exit.')

		while True:
			# Font escape sequences
			if args.plain:
				font_escape_start = ''
				font_escape_end   = ''
			else:
				font_escape_start = '\033[1m' # Boldface
				font_escape_end   = '\033[0m' # Normal

			# Prompt
			try:
				expr_str = input(f'{font_escape_start}epppu expression>{font_escape_end} ')

			# Abort command
			except KeyboardInterrupt:
				print()
				continue

			# Exit
			except EOFError:
				print()
				break

			# Do nothing for empty command
			if expr_str.strip() == '':
				continue

			# Exit
			if expr_str.strip() == 'exit':
				break

			# Clear terminal
			if expr_str.strip() == 'clear':
				os.system('cls' if os.name == 'nt' else 'clear')
				continue

			# Expand prefixes
			expr_str = expand_metric_prefixes(expr_str)

			# Evaluate expression
			try:
				result = eppp.electronic_eval(expr_str)
				if result is None:
					raise SyntaxError('Invalid expression.')

			# Print error and continue
			except Exception as e:
				# Font escape sequences
				if args.plain:
					font_escape_start = ''
					font_escape_end   = ''
				else:
					font_escape_start = '\033[31;1m' # Boldface red
					font_escape_end   = '\033[37;0m' # Normal white

				# Print error message
				msg_lines = traceback.format_exc().splitlines()
				for msg_line in msg_lines[0:-1]:
					print(msg_line)
				print(f'{font_escape_start}{msg_lines[-1]}{font_escape_end}')

				continue

			# Print result
			eppp.inout.print_sci(result)

	# Non-interactive mode
	else:
		# Make string from arguments
		expr_str = ' '.join(args.expression)

		# Expand prefixes again (since additional spaces where introduced)
		expr_str = expand_metric_prefixes(expr_str)

		# Print result
		eppp.inout.print_sci(eppp.electronic_eval(expr_str))

#===========================
# 'make-resistance' command
#===========================
# TODO: Add frequency and support for inductors and capacitors?
# TODO: Switches for what to print

if cmd == 'make-resistance':
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
		'--num-components',
		type    = int,
		nargs   = '?',
		default = -1,
		help    = 'Maximum number of components for the resulting network. Negative values yield no limit. (default: %(default)s)',
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
		help    = 'Minimum resistance used when generating the series. [Ω] (default: %(default)s)',
	)

	parser.add_argument(
		'-Mr',
		'--max-resistance',
		type    = float,
		default = 10e6,
		help    = 'Maximum resistance used when generating the series. [Ω] (default: %(default)s)',
	)

	parser.add_argument(
		'-T',
		'--topology',
		type    = str,
		default = 'mixed',
		help    = 'Valid topologies for the generated network. (mixed, parallel or any) (default: %(default)s)',
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

	# Get the expression
	expr = eppp.make_resistance(
		args.target,
		avail_vals    = eppp.get_avail_vals(args.series, min_val=args.min_resistance, max_val=args.max_resistance),
		tolerance     = args.tolerance,
		max_num_comps = args.num_components,
		topology = args.topology,
	)
	res = expr.evaluate()

	# Print error
	print(str(expr) + (' = '+ eppp.str_sci(res) if args.omit_result else ''))
	if args.print_error:
		eppp.print_sci(
			(res - args.target) / args.target,
			name = 'relative error',
		)

#====================
# 'parallel' command
#====================

if cmd == 'parallel':
	parser = ap.ArgumentParser(
		description = 'Calculates the equivalent impedance of a set of parallel connected components.'
	)

	parser.add_argument(
		'values',
		type  = complex,
		nargs = '+',
		help = 'List of parallel impedances. [Ω]'
	)

	vals = parser.parse_args().values

	# Do the calculation
	res = eppp.parallel_impedance(*vals)

	# Print the result
	eppp.print_sci(res, unit='Ω')

#=====================
# 'reactance' command
#=====================

if cmd == 'reactance':
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
		help = 'Component value. [H or F]',
	)

	parser.add_argument(
		'frequency',
		type = float,
		help = 'Frequency. [Hz]',
	)

	args = parser.parse_args()

	# Determine type of reactive component
	if args.type == 'inductor'[:len(args.type)]:
		res = eppp.inductor_impedance(args.value, args.frequency)
	elif args.type == 'capacitor'[:len(args.type)]:
		res = eppp.capacitor_impedance(args.value, args.frequency)
	else:
		raise ValueError("Argument 2 must be either 'inductor' or 'capacitor'.")

	# Print the result
	eppp.print_sci(res.imag, unit='Ω')

#=======================
# 'susceptance' command
#=======================

if cmd == 'susceptance':
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
		help = 'Component value. [H or F]',
	)

	parser.add_argument(
		'frequency',
		type = float,
		help = 'Frequency. [Ω]',
	)

	args = parser.parse_args()

	# Determine type of reactive component
	if args.type == 'inductor'[:len(args.type)]:
		res = eppp.inductor_admittance(args.value, args.frequency)
	elif args.type == 'capacitor'[:len(args.type)]:
		res = eppp.capacitor_admittance(args.value, args.frequency)
	else:
		raise ValueError("Argument 2 must be either 'inductor' or 'capacitor'.")

	# Print the result
	eppp.print_sci(res.imag, unit='S')

#============================
# 'voltage-division' command
#============================

if cmd == 'voltage-division':
	parser = ap.ArgumentParser(
		description = 'Calculates the voltage divided over series-connected impedances.'
	)

	parser.add_argument(
		'voltage',
		type = complex,
		help = 'Source voltage. [V]',
	)

	parser.add_argument(
		'main_impedance',
		type = complex,
		help = 'Main impedance. [Ω]',
	)

	parser.add_argument(
		'impedances',
		type  = complex,
		nargs = '*',
		help = 'List of other series-connected impedances. [Ω]'
	)

	args = parser.parse_args()
	main_imp = parser.parse_args().main_impedance
	imps     = parser.parse_args().impedances

	# Do the calculation
	res_voltage = eppp.voltage_division(
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
	parser = ap.ArgumentParser(
		description = 'Calculates the current divided between parallel-connected impedances.'
	)

	parser.add_argument(
		'current',
		type = complex,
		help = 'Source current. [A]',
	)

	parser.add_argument(
		'main_impedance',
		type = complex,
		help = 'Main impedance. [Ω]',
	)

	parser.add_argument(
		'impedances',
		type  = complex,
		nargs = '*',
		help = 'List of other parallel-connected impedances. [Ω]'
	)

	args = parser.parse_args()

	# Do the calculation
	current = eppp.current_division(
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
		help = 'Frequency. [Hz]',
	)

	parser.add_argument(
		'-reps',
		'--relative-permittivity',
		type    = float,
		default = 1,
		nargs   = '?',
		help    = 'Relative permittivity of the conductor. (default: %(default)s)'
	)

	parser.add_argument(
		'-rmu',
		'--relative-permeability',
		type    = float,
		default = 1,
		nargs   = '?',
		help    = 'Relative permeability of the conductor. (default: %(default)s)'
	)

	args = parser.parse_args()

	# Do the calculation
	depth = eppp.skin_depth(
		args.resistivity,
		args.frequency,
		rel_permittivity = args.relative_permittivity,
		rel_permeability = args.relative_permeability,
	)

	# Print the result
	eppp.print_sci(depth, unit='m')

#======================
# 'wavelength' command
#======================

if cmd == 'wavelength':
	parser = ap.ArgumentParser(
		description = 'Calculates the wavelength of an electromagnetic wave.'
	)

	parser.add_argument(
		'frequency',
		type = float,
		help = 'Frequency. [Hz]',
	)

	parser.add_argument(
		'-reps',
		'--relative-permittivity',
		type    = float,
		default = None,
		nargs   = '?',
		help    = 'Relative permittivity of the medium. (default: 1)'
	)

	parser.add_argument(
		'-rmu',
		'--relative-permeability',
		type    = float,
		default = None,
		nargs   = '?',
		help    = 'Relative permeability of the medium. (default: 1)'
	)

	parser.add_argument(
		'-s',
		'--speed',
		type    = float,
		default = None,
		nargs   = '?',
		help    = 'Speed of the wave in medium. [m/s]'
	)

	args = parser.parse_args()

	# Do the calculation
	length = eppp.wavelength(
		args.frequency,
		rel_permittivity = args.relative_permittivity,
		rel_permeability = args.relative_permeability,
		speed            = args.speed
	)

	# Print the result
	eppp.print_sci(length, unit='m')

#===========================
# 'wire-resistance' command
#===========================

if cmd == 'wire-resistance':
	parser = ap.ArgumentParser(
		description = 'Calculates the resistance of a wire. Takes the skin effect into account, but uses the approximation that either radius >> skin depth or skin depth >> radius.'
	)

	parser.add_argument(
		'resistivity',
		type = float,
		help = 'Resistivity of the wire. [Ω/m]'
	)

	parser.add_argument(
		'radius',
		type = float,
		help = 'Radius of the wire. [m]',
	)

	parser.add_argument(
		'length',
		type = float,
		help = 'Length of the wire. [m]',
	)

	parser.add_argument(
		'frequency',
		type    = float,
		default = 0,
		nargs   = '?',
		help    = 'Frequency. [Hz] (default: %(default)s)',
	)

	parser.add_argument(
		'-reps',
		'--relative-permittivity',
		type    = float,
		default = 1,
		nargs   = '?',
		help    = 'Relative permittivity of the medium. (default: %(default)s)'
	)

	parser.add_argument(
		'-rmu',
		'--relative-permeability',
		type    = float,
		default = 1,
		nargs   = '?',
		help    = 'Relative permeability of the medium. (default: %(default)s)'
	)

	args = parser.parse_args()

	# Do the calculation
	resistance = eppp.wire_resistance(
		args.resistivity,
		args.radius,
		args.length,
		freq             = args.frequency,
		rel_permittivity = args.relative_permittivity,
		rel_permeability = args.relative_permeability,
	)

	# Print the result
	eppp.print_sci(resistance, unit='Ω')

#==============================
# 'plates-capacitance' command
#==============================

if cmd == 'plates-capacitance':
	parser = ap.ArgumentParser(
		description = 'Calculates the capacitance of two aligned parallel plates of equal area. Assumes plate dimension >> place separation and hence ignores fringe capacitance.'
	)

	parser.add_argument(
		'area',
		type = float,
		help = 'Area of the plates. [m²]'
	)

	parser.add_argument(
		'separation',
		type = float,
		help = 'Distance between the two plates. [m]'
	)

	parser.add_argument(
		'-reps',
		'--relative-permittivity',
		type    = float,
		default = 1,
		nargs   = '?',
		help    = 'Relative permittivity of the medium. (default: %(default)s)'
	)

	args = parser.parse_args()

	# Do the calculation
	cap = eppp.plates_capacitance(
		args.area,
		args.separation,
		rel_permittivity = args.relative_permittivity,
	)

	# Print the result
	eppp.print_sci(cap, unit='F')
