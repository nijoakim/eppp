#!/usr/bin/python3

# Copyright 2014-2016 Joakim Nilsson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# TODO: Parser should understand prefixes?
# TODO: Possibility to switch off print_sci
# TODO: Possibility to omit unit
# TODO: --plain for plainer output text
# TODO: --color for colored parentheses?

#=========
# Imports
#=========

# External
import argparse as ap
import re
import sys
import operator as op

# Internal
import eppp
import eppp.calc

#=========
# Printer
#=========

_print_prefix = True

def _util_print():
	pass

#========
# Parser
#========

# Availible sub-commands
_CMDS = [
	'impedance',
	'network',
	'parallel',
]

# Description
desc_str = 'Executes a command based on the functionality provided by the eppp library. Available commands are: %s.' % ', '.join(map(lambda x: "'"+ x +"'", _CMDS))

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
parser.add_argument('command-arguments', nargs=ap.REMAINDER)
global_args = parser.parse_args()

# Set default significant figures
eppp.set_default_str_sci_args(num_sig_figs=global_args.significant_figures)

# Match input command with available command
cmd_in = global_args.command
pred = re.compile(cmd_in +'.*')
matches = []
for matchcmd in _CMDS:
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

#=====================
# 'impedance' command
#=====================
# TODO: Comment

if cmd == 'impedance':
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

	# TODO: Do not require whole words
	if args.type == 'inductor':
		res = eppp.calc.inductor_imp(args.value, args.frequency)
	elif args.type == 'capacitor':
		res = eppp.calc.capacitor_imp(args.value, args.frequency)
	else:
		# TODO: Error
		pass

	# Print the result
	eppp.print_sci(res, unit='Ω')

#===================
# 'network' command
#===================
# TODO: Add frequency and support for inductors and capacitors?
# TODO: Switches for what to print

if cmd == 'network':
	# Parse
	parser = ap.ArgumentParser(
		description = 'Finds a network of passive components matching a specified (possibly complex) value.'
	)
	parser.add_argument(
		'target',
		type = complex,
		help = 'Target impedance.',
	)
	parser.add_argument(
		'-e',
		'--error',
		type    = float,
		nargs   = '?',
		default = 0.01,
		help    = 'Maximum relative error for the resulting network. (default: %(default)s)',
	)
	parser.add_argument(
		'-c',
		'--components',
		type    = float,
		nargs   = '?',
		default = None,
		help    = 'Maximum number of components for the resulting network. (default: infinity)',
	)
	parser.add_argument(
		'-s',
		'--series',
		default = 'E6',
		help    = 'E-series from which to get available components. (E3, E6, E12, E24, E48, E96 or E192) (default: %(default)s)',
	)
	parser.add_argument(
		'--configuration',
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

	# TODO: Move this inside lumped_network?
	# Generate list of operations
	if args.configuration == 'any':
		ops = [eppp.calc.parallel_imp, op.add]
	elif args.configuration == 'series':
		ops = [op.add]
	elif args.configuration == 'parallel':
		ops = [eppp.calc.parallel_imp]
	else:
		pass
		# TODO: Error

	# Get the expression
	expr = eppp.calc.lumped_network(
		args.target,
		avail_vals    = eppp.calc.get_avail_vals(args.series),
		max_rel_error = args.error,
		max_num_comps = args.components,
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
	res = eppp.calc.parallel_imp(*vals)

	# Print the result
	eppp.print_sci(res, unit='Ω')
