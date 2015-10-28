#!/usr/bin/python3

# Copyright 2014-2015 Joakim Nilsson
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

import __init__ as eppp
import argparse
import re
import sys

CMDS = [
	'parallel',
	'pskabb',
]

def _make_cmds_str(cmds):
	cmds_str = ''
	for cmd in cmds:
		cmds_str += '\t%s\n' % cmd
	return cmds_str

descriptionStr = 'Executes a command provided by the eppp. Avaliable commands are:\n%s' % _make_cmds_str(CMDS)

# Parse input command
parser = argparse.ArgumentParser(description=descriptionStr)
parser.add_argument('command')
parser.add_argument('command-arguments', nargs='*')
cmd_in = parser.parse_args().command

# Match input command with available command
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

# Remove command argument from argv
del sys.argv[1]

# TODO: Add descriptions for commands

# ================
# parallel command
# ================

if cmd == 'parallel':
	# Parse
	parser = argparse.ArgumentParser()
	parser.add_argument('values', type=complex, nargs='+')
	vals = parser.parse_args().values
	
	# Do the calculation
	res = eppp.parallel_imp(*vals)
	
	# Convert to weakest type for nicer printing
	if res.imag == 0:
		res = res.real
		if res == int(res):
			res = int(res)
	
	# Print the result
	print(res)

# TODO: Command to calculate impedance of inductor or capacitor at a given frequency
