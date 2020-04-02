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
import unittest as ut
from math import inf

# Internal
import eppp
import eppp.calc

#=========
# Logging
#=========

# Do not log anything
eppp.set_log_level(0)

#============
# Unit tests
#============

class TestStringMethods(ut.TestCase):
	# TODO: Test electronic_eval

	def test_make_impedance(self):
		# Lower than available values
		self.assertEqual(
			str(eppp.calc.make_impedance(5)),
			'(10.00 || 10.00)'
		)

		# Higher than available values
		self.assertEqual(
			str(eppp.calc.make_impedance(20e6)),
			'(10.00 M + 10.00 M)'
		)

		# 1 component
		self.assertEqual(
			str(eppp.calc.make_impedance(88120, max_num_comps=1)),
			'100.0 k'
		)

		# 2 components
		self.assertEqual(
			str(eppp.calc.make_impedance(88120, max_num_comps=2)),
			'(680.0 k || 100.0 k)'
		)

		# 3 components
		self.assertEqual(
			str(eppp.calc.make_impedance(88120, max_num_comps=3)),
			'(220.0 k || (47.00 k + 100.0 k))'
		)

		# 3 components, solved by 2
		self.assertEqual(
			str(eppp.calc.make_impedance(16800, max_num_comps=3, tolerance=0)),
			'(6.800 k + 10.00 k)'
		)

	def test_parallel_impedance(self):
		self.assertEqual(eppp.calc.parallel_impedance(3, 3, 3), 1)        # Three elements
		self.assertEqual(eppp.calc.parallel_impedance(1), 1)              # One element
		self.assertEqual(eppp.calc.parallel_impedance(1, 1j), 0.5 + 0.5j) # Complex numbers
		self.assertEqual(eppp.calc.parallel_impedance(1, 2), 2/3)         # Floating point
		self.assertEqual(eppp.calc.parallel_impedance(1, 0), 0)           # Zero
		self.assertEqual(eppp.calc.parallel_impedance(1, inf), 1)         # Infinity

	def test_decibel(self):
		# Power
		self.assertEqual(eppp.calc.convert_to_db(100, db_type='power'), 20)   # To dB
		self.assertEqual(eppp.calc.convert_from_db(20, db_type='power'), 100) # From dB
		
		# Amplitude
		self.assertEqual(eppp.calc.convert_to_db(100, db_type='amplitude'), 40)   # To dB
		self.assertEqual(eppp.calc.convert_from_db(40, db_type='amplitude'), 100) # From dB

	def test_sci_notation(self):
		# Correct number of significant figures
		eppp.set_default_str_sci_args(num_sig_figs=3)
		self.assertEqual(eppp.str_sci(1e6), '1.00 M')
		self.assertEqual(eppp.str_sci(1e6, num_sig_figs=5), '1.0000 M')
		self.assertEqual(eppp.str_sci(111.111e6), '111 M')
		self.assertEqual(eppp.str_sci(11.1111e6), '11.1 M')

		# Rounding
		self.assertEqual(eppp.str_sci(1005), '1.01 k')

		# Unit naming
		self.assertEqual(eppp.str_sci(1e+3,  unit = 'm'), '1.00 km')

		# Metric style
		self.assertEqual(eppp.str_sci(1e+3 ), '1.00 k')
		self.assertEqual(eppp.str_sci(1e-3 ), '1.00 m')
		self.assertEqual(eppp.str_sci(1e+24), '1.00 Y')
		self.assertEqual(eppp.str_sci(1e-24), '1.00 y')
		self.assertEqual(eppp.str_sci(1e+27), '1.00e27')
		self.assertEqual(eppp.str_sci(1e-27), '1.00e-27')

		# TODO: Scientific style
		# TODO: Engineering style

		# Complex numbers
		self.assertEqual(eppp.str_sci(   1 +    1j),  '(1.00 + j1.00)')
		self.assertEqual(eppp.str_sci(   1 -    1j),  '(1.00 - j1.00)')
		self.assertEqual(eppp.str_sci(  -1 -    1j), '(-1.00 - j1.00)')
		self.assertEqual(eppp.str_sci(          1j),          'j1.00')
		self.assertEqual(eppp.str_sci(         -1j),         '-j1.00')
		self.assertEqual(eppp.str_sci(1000 +   10j),  '(1.00 + j0.01) k')
		self.assertEqual(eppp.str_sci(  10 + 1000j),  '(0.01 + j1.00) k')
		self.assertEqual(eppp.str_sci(1000 +    1j),          '1.00 k')

ut.main(exit = False)
