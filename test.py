# Copyright 2015 Joakim Nilsson
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

# from eppp import *
from __init__ import *
import debug as _dbg
import inout as _inout
import pylab as _pl

set_log_level(0)

# Lumped find tests
import time
import cProfile

# t = time.time()
# bc = lumped_network(88123, max_num_comps = 3)
# cProfile.run('lumped_network(88123, max_num_comps = 3)')
# _dbg.printVar(time.time() - t, 'time')
from calc_lumped_network import _polish_eval
# print(_polish_eval(bc))
# print(bc)

import unittest as ut

class TestStringMethods(ut.TestCase):
	# def test_lumped_network(self):
	# 	self.assertEqual(lumped_network(88123, max_num_comps = 3), bc)
	
	def test_parallel_imp(self):
		self.assertEqual(parallel_imp(3, 3, 3), 1)          # Three elements
		self.assertEqual(parallel_imp(1), 1)                # One element
		self.assertEqual(parallel_imp(1, 1j), (0.5 + 0.5j)) # Complex numbers
		self.assertEqual(parallel_imp(1, 2), 2/3)           # Floating point
	
	def test_decibel(self):
		# Amplitude
		self.assertEqual(convert_db(100),                 40)
		self.assertEqual(convert_db(40, from_db = True), 100)
		
		# Power
		self.assertEqual(convert_db(100, use_power_db = True),                  20)
		self.assertEqual(convert_db(20,  use_power_db = True, from_db = True), 100)
	
	def test_sci_notation(self):
		# Correct number of significant figures
		set_default_sig_figs(3)
		self.assertEqual(str_sci(1e6), '1.00 M')
		self.assertEqual(str_sci(1e6, sig_figs = 5), '1.0000 M')
		self.assertEqual(str_sci(111.111e6), '111 M')
		self.assertEqual(str_sci( 11.1111e6), '11.1 M')
		
		# Rounding
		self.assertEqual(str_sci(1005), '1.01 k')
		
		# Unit naming
		self.assertEqual(str_sci(1000), unit = 'm'), '1.00 km')

ut.main()
