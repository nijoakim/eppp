# Copyright 2015-2019 Joakim Nilsson
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#=========
# Imports
#=========

# External
import time

# Internal
import eppp
import eppp.calc

#==================
# Helper functions
#==================

_t = 0

def _print_test(s):
	print()
	print('-' * len(s))
	print()
	print(s)
	print()

def _reset_clock():
	global _t
	_t = time.time()

def _print_clock():
	global _t
	eppp.print_sci(
		time.time() - _t,
		quantity = 'duration',
		unit = 's',
	)
	print()

#=============
# Speed tests
#=============

# Lumped network

# 3 components
_print_test('lumped_network, 3 components')
_reset_clock()
eppp.calc.lumped_network(
	88120,
	max_num_comps = 3,
	max_rel_error = 0,
)
_print_clock()

# 4 components
_print_test('lumped_network, 4 components')
_reset_clock()
eppp.calc.lumped_network(
	88120,
	max_num_comps = 4,
	max_rel_error = 0,
)
_print_clock()

# 5 components
_print_test('lumped_network, 5 components')
_reset_clock()
eppp.calc.lumped_network(
	88120,
	max_num_comps = 5,
	max_rel_error = 0,
)
_print_clock()
