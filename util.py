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

def _makeCmdsStr(cmds):
	cmdsStr = ''
	for cmd in cmds:
		cmdsStr += '\t%s\n' % cmd
	return cmdsStr

descriptionStr = 'Executes a command provided by the eppp. Avaliable commands are:\n%s' % _makeCmdsStr(CMDS)

# Parse input command
parser = argparse.ArgumentParser(description=descriptionStr)
parser.add_argument('command')
parser.add_argument('command-arguments', nargs='*')
cmdIn = parser.parse_args().command

# Match input command with available command
pred = re.compile(cmdIn +'.*')
matches = []
for matchcmd in CMDS:
	if pred.match(matchcmd) is not None:
		matches.append(matchcmd)
		cmd = matchcmd
numMatches = len(matches)
	
# Check for mismatches and ambiguities
if numMatches == 0:
	sys.stderr.write("'%s' does not match any command.\n" % cmdIn)
	exit(1)
elif numMatches == 2:
	cmdsStr = makeCmdsStr(matches)
	sys.stderr.write('%s is ambiguous.\n\nDid you mean any of these commands?\n%s\n' % (cmdIn, cmdsStr))
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
	res = eppp.parallelRes(*vals)
	
	# Convert to weakest type for nicer printing
	if res.imag == 0:
		res = res.real
		if res == int(res):
			res = int(res)
	
	# Print the result
	print(res)

