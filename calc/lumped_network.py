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
import functools as _ft
import itertools as _it
import operator  as _op
import pylab     as _pl

# Internal
from ..error import _string_or_exception
from ..log   import _log
from ..debug import *
from ..inout import str_sci as _str_sci

#=======
# Other
#=======

class ExprTree:
	def __init__(
			self,
			polish_expr,
			is_reverse  = False,
			do_consume  = False,
			do_simplify = True,
			unit        = '',
		):
		# Do not modify expression unless explicitly stated
		if not do_consume:
			polish_expr = list(polish_expr)

		# Check so that a valid expression format has been given
		if not is_reverse:
			polish_expr.reverse()

		# Unit for printing
		self._unit = unit

		# Operator and operands for this node
		self.operator = None
		self.operands = []

		# Consume polishly
		el = polish_expr.pop()
		if callable(el): # If not leaf
			self.operator = el

			# Append the two operands
			for i in range(2):
				self.operands.append(ExprTree(
					polish_expr,
					do_consume = True,
					is_reverse = True,
					unit       = self._unit,
				))
		else: # If leaf
			self.operands.append(el)

		# Simplify
		if do_simplify:
			self.simplify()

	def __str__(self):
		if self._is_leaf():
			return _str_sci(self.operands[0], unit = self._unit)
		else:
			# Use symbols for some functions
			symbol_dict = {
				_op.add:         '+' ,
				parallel_imp:    '||',
				_parallel_imp_non_strict: '||',
			}
			op_sym = symbol_dict[self.operator] if self.operator in symbol_dict else str(self.operator)

			# Form expression
			ret = ''
			for operand in self.operands[:-1]:
				ret += str(operand) +' '+ op_sym +' '
			ret += str(self.operands[-1])

			return '('+ ret +')'

	def _is_leaf(self):
		return self.operator is None

	def _getSize(self):
		if self._is_leaf():
			# Leaf size = 1
			return 1
		else:
			# Add size of children
			ret = 0
			for operand in self.operands:
				ret += operand._getSize()
			return ret

	def simplify(self):
		if not self._is_leaf():
			# Build new operands
			new_operands = []
			for operand in self.operands:
				# Simplify child
				operand.simplify()

				# Steal child's operands if it is of the same type of operand as this one
				if \
					not operand._is_leaf() \
					and operand.operator is self.operator \
					:
					new_operands.extend(operand.operands)
				
				# Add unmodified operand otherwise
				else:
					new_operands.append(operand)

			# Sort operands by size
			new_operands.sort(key = lambda x: x._getSize())

			# Update data
			self.operands = new_operands

	def evaluate(self):
		if self._is_leaf():
			return self.operands[0]
		else:
			return _ft.reduce(self.operator, map(lambda x: x.evaluate(), self.operands))

def _doc_reactive_comp_imp(quantity):
	return """
	Calculates the impedance of an inductor for a given frequency.

	Args:
		%s (number): %s
		freq (number):       %sFrequency

	Returns:
		The impedance for an inductor with the specified %s at the specified frequency.
	""" % (
		quantity,
		quantity[0].upper() + quantity[1:],        # First letter upper-case
		' ' * (len(quantity) - len('inductance')), # For alignment
		quantity,
	)

def inductor_imp(inductance, freq):
	return inductance * 1j * 2 * _pl.pi * freq

def capacitor_imp(capacitance, freq):
	return 1 / (capacitance * 1j * 2 * _pl.pi * freq)

inductor_imp.__doc__  = _doc_reactive_comp_imp("inductance")
capacitor_imp.__doc__ = _doc_reactive_comp_imp("capacitance")

def parallel_imp(*vals):
	"""
	Calculates the equivalent impedance of a set of parallel connected components.

	Args:
		*vals (number): Parallel connected impedances.

	Returns:
		The equivalent impedance for all '*vals' impedances connected in parallel.
	"""

	# Sum admittances
	admittance = 0
	try:
		for val in vals:
			admittance += 1 / val

	# Return 0 if there is at least one 0 impedance
	except ZeroDivisionError:
		return 0

	# Return equivalent impedance
	try:
		return 1 / admittance

	# Return infinity if total admittance is 0
	except ZeroDivisionError:
		return float('inf')

# Same as the above function, but only takes 2 arguments and assumes non-zero, finite impedances and is thus faster
def _parallel_imp_non_strict(z1, z2):
	return z1*z2 / (z1 + z2)

def get_avail_vals(
		series    = 'E6',
		min_val   = 10,
		max_val   = 10e6,
		comp_type = 'resistor',
		freq      = None,
	):
	"""
	Generates a list of resistors based on a standard series.


	Kwargs:
		series (string):    (Default: 'E6') Series to generate from. ('E3', 'E6', 'E12', 'E24', 'E48', 'E96' or 'E192')
		min_val (float):    (Default: 10)   Minimum value to be included in the generated series.
		max_val (float):    (Default: 10e6) Maximum value to be included in the generated series.
		comp_type (string): (Default: 'resistor') Type of components to generate. ('resistor', 'capacitor' or 'inductor')
		freq (float):       Frequency at which impedances for reactive components are calculated.

	Returns:
		[complex]. Impedances of available components from the specified series.
	"""

	# Component type setting
	if not comp_type in ['resistor', 'capacitor', 'inductor']:
		raise Exception("'comp_type' must be either 'resistor', 'capacitor' or 'inductor'.")
	if comp_type in ['capacitor', 'inductor'] and freq == None:
		raise Exception("'freq' must be specified if '%s' is chosen as component type." % comp_type)

	# Derives an E-series from a higher one
	def _derive_series(series_num, orig_series):
		skip = len(orig_series) / series_num
		return [el for i, el in enumerate(orig_series) if i % skip == 0]

	# Dictionary with common series
	avail_vals_dict = {}

	# Longest 2-digit series
	avail_vals_dict['E24'] = [
		10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27, 30,
		33, 36, 39, 43, 47, 51, 56, 62, 68, 75, 82, 91,
	]

	# Longest 3-digit series
	avail_vals_dict['E192'] = [
		100, 101, 102, 104, 105, 106, 107, 109, 110, 111, 113, 114,
		115, 117, 118, 120, 121, 123, 124, 126, 127, 129, 130, 132,
		133, 135, 137, 138, 140, 142, 143, 145, 147, 149, 150, 152,
		154, 156, 158, 160, 162, 164, 165, 167, 169, 172, 174, 176,
		178, 180, 182, 184, 187, 189, 191, 193, 196, 198, 200, 203,
		205, 208, 210, 213, 215, 218, 221, 223, 226, 229, 232, 234,
		237, 240, 243, 246, 249, 252, 255, 258, 261, 264, 267, 271,
		274, 277, 280, 284, 287, 291, 294, 297, 301, 305, 309, 312,
		316, 320, 324, 328, 332, 336, 340, 344, 348, 352, 357, 361,
		365, 370, 374, 379, 383, 388, 392, 397, 402, 407, 412, 417,
		422, 427, 432, 437, 442, 448, 453, 459, 464, 470, 475, 481,
		487, 493, 499, 505, 511, 517, 523, 530, 536, 542, 549, 556,
		562, 569, 576, 583, 590, 597, 604, 612, 619, 626, 634, 642,
		649, 657, 665, 673, 681, 690, 698, 706, 715, 723, 732, 741,
		750, 759, 768, 777, 787, 796, 806, 816, 825, 835, 845, 856,
		866, 876, 887, 898, 909, 920, 931, 942, 953, 965, 976, 988,
	]

	# Derived series
	avail_vals_dict['E3']  = _derive_series( 3, avail_vals_dict['E24'])
	avail_vals_dict['E6']  = _derive_series( 6, avail_vals_dict['E24'])
	avail_vals_dict['E12'] = _derive_series(12, avail_vals_dict['E24'])
	avail_vals_dict['E48'] = _derive_series(48, avail_vals_dict['E192'])
	avail_vals_dict['E96'] = _derive_series(96, avail_vals_dict['E192'])

	# Get basic available values
	if type(series) is str:
		basic_avail_vals = avail_vals_dict[series]
	else:
		basic_avail_vals = series
	avail_vals = list(basic_avail_vals)

	# Append higher order series
	multiplier = 10
	while avail_vals[-1] <= max_val:
		avail_vals  += map(lambda x: x*multiplier, basic_avail_vals)
		multiplier *= 10

	# Reverse for more efficient list operations
	avail_vals.reverse()
	basic_avail_vals.reverse()

	# Append lower order series
	divider = 10
	while avail_vals[-1] >= min_val:
		avail_vals += map(lambda x: x / divider, basic_avail_vals)
		divider    *= 10

	# Reverse again for ordered list
	avail_vals.reverse()

	# Filter out too high or too low values
	avail_vals = filter(lambda x: x <= max_val, avail_vals)
	avail_vals = filter(lambda x: x >= min_val, avail_vals)

	# Transform values according to the type of component type
	if comp_type == 'resistor':
		comp_specific_func = lambda x: x
	elif comp_type == 'capacitor':
		comp_specific_func = lambda x: capacitor_imp(x, freq)
	elif comp_type == 'inductor':
		comp_specific_func = lambda x: inductor_imp(x, freq)
	avail_vals = map(comp_specific_func, avail_vals)

	return list(avail_vals)

# Optimised way to evaluate polish expressions (faster than going through ExprTree)
# TODO: C-version of this function
def _polish_eval(expr):
	# Do not modify original expression
	expr = list(expr)

	# Start with an empty stack
	stack = []

	# While there are elements left in the expression
	while expr:
		el = expr.pop()

		# If operator
		if callable(el):
			expr.append(el(stack.pop(), stack.pop()))

		# If value
		else:
			stack.append(el)

	# Return the stack in the correct order
	stack.reverse()
	return stack

# Same as the above function, but assumes it will evaluate to 1 element and is therefore faster
def _polish_eval_non_strict(expr):
	# To avoid avoid property lookups
	add = _op.add

	# Copy of original expression
	expr  = list(expr)

	# Indices to avoid using 'pop()'/'append()' for better performance
	i = len(expr) - 2 # Expression index
	j = i-1           # Stack index

	# While there are elements left in the expression
	while i >= 0:
		i -= 1
		el = expr[i]

		# if callable(el):
		# 	j += 2
		# 	expr[i] = el(expr[j-1], expr[j])
		# 	i += 1

		# TODO: Fall back to original function if there are other functions (do this in 'lumped_network')
		# If operator
		if el == _parallel_imp_non_strict:
			j += 1
			expr[j+1] = (expr[j+1] * expr[j]) / (expr[j+1] + expr[j])
		elif el == aaa:
			j += 1
			expr[j+1] = expr[j+1] + expr[j]

		# If value
		else:
			expr[j] = el
			j -= 1

	# Return the stack (no stack reversal since a complete evaluation is assumed)
	return [expr[j+1]]

# TODO: Argument for fraction of maximum dissipated power?
def lumped_network(
		target,
		max_num_comps = float('inf'),
		max_rel_error = None,
		max_abs_error = None,
		avail_vals    = get_avail_vals('E6'),
		avail_ops     = [_parallel_imp_non_strict, _op.add],
	):
	"""
	Finds a network of passive components matching a specified (possibly complex) value.

	Args:
		target (number):        Target impedance for the network.

	Kwargs:
		max_num_comps (int):    Maximum number of components in the network. The function will return a network with no more components than this value.
		max_rel_error (number): (Default 0.01) Maximum tolerable relative error. The relative error of the resulting network will be less than this value if that is possible given 'max_num_comps'.
		max_abs_error (number): Maximum tolerable absolute error. The absolute error of the resulting network will be less than this value if that is possible given 'max_num_comps'.
		avail_vals ([number]):  List of available values of the impedances used in the network.
		avail_ops ([operator]): (Default: [eppp.calc.parallel_imp, operator.add]) List of operators used for calculating the resulting impedance. The operators are represented by a function that takes to arguments. The operators must be associative and commutative.

	Returns:
		ExprTree. Expression tree of the resulting network. Use ExprTree.evaluate() to get it's value.
	"""

	# Determine whether a strict polish_eval function must be used
	polish_eval_func = _polish_eval_non_strict
	for op in avail_ops:
		if  op != _op.add \
		and op != _parallel_imp_non_strict \
		and op != parallel_imp:
			polish_eval_func = _polish_eval
	

	# Use more general parallel function if 'avail_vals' contains 0 or infinity
	if 0 in avail_vals or float('inf') in avail_vals:
		avails_ops = list(map(lambda x: parallel_imp if x == _parallel_imp_non_strict else x))

	# Don't display a unit (may change later)
	# unit = 'Ω'
	unit = ''

	# Check so that target is non-zero
	if target == 0:
		return _string_or_exception("Target impedance must be non-zero.")

	# Figure out error mode
	if max_abs_error is None and max_rel_error is None:
		max_error = 0.01
		use_rel_error = True
	elif not max_abs_error is None and not max_rel_error is None:
		return _string_or_exception("Can not specify both 'max_abs_error' and 'max_rel_error'.")
	elif not max_abs_error is None:
		max_error = max_abs_error
		use_rel_error = False
	else:
		max_error = max_rel_error
		use_rel_error = True

	# Initial values
	best_error = float('inf')
	best_expr  = None

	# For all numbers of components, starting from one up to 'max_num_comps'
	for num_comps in _it.count(1):
		_log(1, 'Finding lumped network for %i component%s...' % (num_comps, '' if num_comps == 1 else 's'))

		# Insertions generator
		def insertions_gen(ops, last_op = None):
			# Base case
			if len(ops) == 0:
				yield []

			# Recurse
			else:
				cur_op = ops[0]
				for insertions in insertions_gen(ops[1:], last_op = cur_op):
					# Avoid redundant insertion variations by not varying operator order in case of consecutive equal operations
					if cur_op == last_op or cur_op == None:
						yield [1] + insertions

					# Non-redundant case
					else:
						yield [0] + insertions
						yield [1] + insertions

		best_signed_error = None
		for values in _it.combinations_with_replacement(avail_vals, num_comps):
			for ops in _it.product(avail_ops, repeat = num_comps - 1):
				for insertions in insertions_gen(ops):
					# Initilize expression and insert position
					expr = list(values)
					insert_pos = 0

					# Insert functions in expression in every valid way except in redundant ways
					op_list = list(ops)
					for insertion in insertions:
						expr.insert(insert_pos, op_list.pop())
						insert_pos += insertion + 1

					# Get value from evaluated expression
					# value = ExprTree(expr).evaluate()
					value = polish_eval_func(expr)[0] # Faster than the above

					# Calculate error
					if use_rel_error:
						error = abs((value - target) / target) # Division-by-zero safe since target can not be 0
					else:
						error = abs(value - target)

					# Remember result if best so far
					if error <= best_error:
						best_error        = error
						best_expr         = expr
						best_signed_error = best_error * _pl.sign(value - target)

						# Return if an optimal solution has been found
						if best_error == 0:
							return ExprTree(best_expr, unit = unit)

		# Log best error so far
		if best_signed_error is not None:
			if use_rel_error:
				_log(2, 'Best relative error so far: %s' % (_str_sci(best_signed_error)))
			else:
				_log(2, 'Best absolute error so far: %s' % (_str_sci(best_signed_error)))

		# Log best network
		_log(3, 'Best network so far: '+ str(ExprTree(best_expr, unit = unit)))

		# Return if sufficiently good or maximum number of components have been used
		if best_error <= max_error or num_comps == max_num_comps:
			return ExprTree(best_expr, unit = unit)
