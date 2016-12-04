# Copyright 2015-2016 Joakim Nilsson
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

#=========
# Imports
#=========

# External
import time
import unittest as ut

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
	# TODO: Finish this
	def test_lumped_network(self):
		self.assertEqual(
			str(eppp.calc.lumped_network(88123, max_num_comps = 3)),
			'(220.0 k || (47.00 k + 100.0 k))'
		)

	def test_parallel_imp(self):
		self.assertEqual(eppp.calc.parallel_imp(3, 3, 3), 1)        # Three elements
		self.assertEqual(eppp.calc.parallel_imp(1), 1)              # One element
		self.assertEqual(eppp.calc.parallel_imp(1, 1j), 0.5 + 0.5j) # Complex numbers
		self.assertEqual(eppp.calc.parallel_imp(1, 2), 2/3)         # Floating point

	def test_decibel(self):
		# Amplitude
		self.assertEqual(eppp.calc.convert_to_db(100), 40)   # To dB
		self.assertEqual(eppp.calc.convert_from_db(40), 100) # From dB
		
		# Power
		self.assertEqual(eppp.calc.convert_to_db(100, use_power_db = True), 20)   # To dB
		self.assertEqual(eppp.calc.convert_from_db(20, use_power_db = True), 100) # From dB

	def test_sci_notation(self):
		# Correct number of significant figures
		eppp.set_default_num_sig_figs(3)
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
		self.assertEqual(eppp.str_sci(   1 +    1j),  '1.00 + j1.00')
		self.assertEqual(eppp.str_sci(   1 -    1j),  '1.00 - j1.00')
		self.assertEqual(eppp.str_sci(  -1 -    1j), '-1.00 - j1.00')
		self.assertEqual(eppp.str_sci(          1j),         'j1.00')
		self.assertEqual(eppp.str_sci(         -1j),        '-j1.00')
		self.assertEqual(eppp.str_sci(1000 +   10j),  '1.00 + j0.01 k')
		self.assertEqual(eppp.str_sci(  10 + 1000j),  '0.01 + j1.00 k')
		self.assertEqual(eppp.str_sci(1000 +    1j),          '1.00 k')

ut.main(exit = False)

#=============
# Speed tests
#=============

# Lumped network

# t = time.time()
# eppp.calc.lumped_network(88123, max_num_comps = 3, max_rel_error = 0)
# eppp.print_sci(
# 	time.time() - t,
# 	quantity='lumped_network, 3 components, time',
# 	unit='s'
# )

# t = time.time()
# eppp.calc.lumped_network(88123, max_num_comps = 4, max_rel_error = 0)
# eppp.print_sci(
# 	time.time() - t,
# 	quantity='lumped_network, 4 components, time',
# 	unit='s'
# )
