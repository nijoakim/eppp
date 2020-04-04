# Copyright 2015-2020 Joakim Nilsson
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

_target = 88123.456789

# 2 components
_print_test('make_resistance, 2 components')
_reset_clock()
eppp.calc.make_resistance(
	_target,
	max_num_comps = 2,
	tolerance     = 0,
)
_print_clock()


# 3 components
_print_test('make_resistance, 3 components')
_reset_clock()
eppp.calc.make_resistance(
	_target,
	max_num_comps = 3,
	tolerance     = 0,
)
_print_clock()

# 4 components
_print_test('make_resistance, 4 components')
_reset_clock()
eppp.calc.make_resistance(
	_target,
	max_num_comps = 4,
	tolerance     = 0,
)
_print_clock()

# 5 components
_print_test('make_resistance, 5 components')
_reset_clock()
eppp.calc.make_resistance(
	_target,
	max_num_comps = 5,
	tolerance     = 0,
)
_print_clock()

# 6 components
_print_test('make_resistance, 6 components')
_reset_clock()
eppp.calc.make_resistance(
	_target,
	max_num_comps = 6,
	tolerance     = 0,
)
_print_clock()

# 7 components
_print_test('make_resistance, 7 components')
_reset_clock()
eppp.calc.make_resistance(
	_target,
	max_num_comps = 7,
	tolerance     = 0,
)
_print_clock()

# 6 components
_print_test('make_resistance, 8 components')
_reset_clock()
eppp.calc.make_resistance(
	_target,
	max_num_comps = 8,
	tolerance     = 0,
)
_print_clock()
