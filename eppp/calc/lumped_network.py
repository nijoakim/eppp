# Copyright 2015-2020 Joakim Nilsson
# Copyright 2016-2017 Jimmy Nyström
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
import ast       as _ast
import functools as _ft
import itertools as _it
import operator  as _op
import numpy     as _np
from bisect import bisect
from math   import inf, nan

# Internal
from ..debug import *
from ..inout import str_sci as _str_sci
from ..log   import _log

#=======
# Other
#=======

# String representation for functions decorator
def _func_str(str_):
	def decorator(func):
		func.str = str_
		return func
	return decorator

# TODO: Document
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
			if self.operator is _op.add:
				op_sym = '+'
			else:
				op_sym = self.operator.str if hasattr(self.operator, 'str') else str(self.operator)

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

# Docstring decorator for 'inductor_impedance' and 'capacitor_impedance'.
def _doc_reactive_comp_imp(quantity):
	def decorator(func):
		func.__doc__ = """
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
		return func
	return decorator

@ _doc_reactive_comp_imp('inductance')
def inductor_impedance(ind, freq):
	return ind * 1j * 2 * _np.pi * freq

@ _doc_reactive_comp_imp('capacitance')
def capacitor_impedance(cap, freq):
	if cap == 0 or freq == 0:
		return -1j * inf
	else:
		return 1 / (cap * 1j * 2 * _np.pi * freq)

# TODO: Move to proper place
# TODO: Add to utils
def voltage_division(voltage, imp_main, *imps):
	"""
	Calculates the voltage divided over series connected impedances.

	Args:
		voltage (number):  Source voltage. [V]
		imp_main (number): Main impedance. [Ω]
		*imps (number):    Other series connected impedances. [Ω]

	Returns:
		The voltage arising over 'imp_main' when 'main_imp' is connected in series with 'imps' with 'voltage' volts over them. [V]
	"""

	# Total impedance
	imp_total = imp_main + sum(imps)

	try:
		return voltage * imp_main / imp_total

	except ZeroDivisionError:
		if voltage * imp_main == 0:
			return nan
		else:
			return _np.sign(voltage * imp_main) * inf

# TODO: inductor_admittance, capacitor_admittance

@_func_str('||')
def parallel_impedance(*vals):
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
		return inf

def series_adm(*vals):
	"""
	Calculates the equivalent admittance of a set of series connected components.

	Args:
		*vals (number): Series connected admittances.

	Returns:
		The equivalent admittance for all '*vals' admittances connected in series.
	"""
	return parallel_impedance(*vals)

def electronic_eval(expr):
	OPERATORS = {
		_ast.Add:      _op.add,
		_ast.Sub:      _op.sub,
		_ast.USub:     _op.neg,
		_ast.Mult:     _op.mul,
		_ast.Div:      _op.truediv,
		_ast.Pow:      _op.pow,
		_ast.FloorDiv: parallel_impedance,
	}
	# TODO: Docstring

	expr = expr.replace('||', '//') # Accept both kinds of parallel connection symbols
	expr = expr.replace('**', 'a')  # Will result in error (which is intended)
	expr = expr.replace('^', '**')   # Use '^' for exponentiation

	# Evaluates the parsed abstract syntax tree
	def eval_ast(node):
		if isinstance(node, _ast.Num):
			return node.n
		elif isinstance(node, _ast.BinOp):
			return OPERATORS[type(node.op)](eval_ast(node.left), eval_ast(node.right))
		elif isinstance(node, _ast.UnaryOp):
			return OPERATORS[type(node.op)](eval_ast(node.operand))

	try:
		return eval_ast(_ast.parse(expr, mode='eval').body)
	except:
		raise Exception('Invalid expression.') # TODO: Proper exception type

# Same as the above function, but only takes 2 arguments and assumes non-zero, finite impedances and is thus faster
@_func_str('||')
def _parallel_impedance_non_strict(z1, z2):
	return z1*z2 / (z1 + z2)

# Sums two numbers (for series impedance calculations)
@_func_str('+')
def _add(x1, x2):
	return x1 + x2

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
		[number]. Impedances of available components from the specified series.
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
		comp_specific_func = lambda x: capacitor_impedance(x, freq)
	elif comp_type == 'inductor':
		comp_specific_func = lambda x: inductor_impedance(x, freq)
	avail_vals = map(comp_specific_func, avail_vals)

	return list(avail_vals)

# Optimised way to evaluate polish expressions (faster than going through ExprTree)
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

# Same as the above function but with these differences:
# - Assumes complete evaluation to exactly one element
# - Does not preserve 'expr'
# - Assumes the only functions are '_parallel_impedance_non_strict' and '_add'
# - Extra argument for pre-calculated list length
# def polish_eval_non_strict(expr):

# Import and initialize C version of '_polish_eval_non_strict'
try:
	from ..fast_misc import polish_eval_non_strict      as _polish_eval_non_strict
	from ..fast_misc import polish_eval_non_strict_init as _polish_eval_non_strict_init
	_polish_eval_non_strict_init(_parallel_impedance_non_strict, _add)

# Fall back to Python version of 'polish_eval_non_strict' if C version can not be imported
except ImportError:
	def _polish_eval_non_strict(expr):
		# Indices to avoid using 'pop()'/'append()' for better performance
		i = len(expr) - 2 # Expression pointer
		j = i - 1         # Stack pointer

		# While there are elements left in the expression
		while i > 0:
			i -= 1
			el = expr[i]

			# If parallel operator
			if el == _parallel_impedance_non_strict:
				j += 1
				k = j + 1
				a = expr[k]
				b = expr[j]
				expr[k] = (a * b) / (a + b)

			# If series operator
			elif el == _add:
				j += 1
				expr[j+1] = expr[j+1] + expr[j]

			# If value
			else:
				expr[j] = el
				j -= 1

		# Return the stack (no stack reversal since a complete evaluation is assumed)
		return expr[j+1]

def lumped_network(
		target,
		max_num_comps  = inf,
		max_rel_error  = None, # TODO: Use
		max_abs_error  = None,
		avail_vals     = get_avail_vals('E6'),
		pre_calc_depth = 0, # TODO: Fails unit tests if > 0
	):
	# TODO: Does not work with complex values

	max_abs_error = 0.001 # TODO: Do it properly

	# Pre-calculated equivalent impedances from polish expressions
	pre_calc = {}

	# Base case for pre-calculated values
	for val in avail_vals:
		pre_calc[val] = [val]

	# Pre-calculate values
	for i in range(1, min(pre_calc_depth, max_num_comps)):
		next_pre_calc = {}
		for val in avail_vals:
			for pre_calc_val in pre_calc:
				expr                        = pre_calc[pre_calc_val]
				series_val                  = val + pre_calc_val
				next_pre_calc[series_val]   = [_add, val, *expr]
				parallel_val                = (val * pre_calc_val) / (val + pre_calc_val)
				next_pre_calc[parallel_val] = [parallel_impedance, val, *expr]
		next_pre_calc.update(pre_calc)
		pre_calc = next_pre_calc
	pre_calc_keys = sorted(pre_calc.keys())

	# Loop up to maximum number of components
	for i in _it.count() if max_num_comps == inf else range(max_num_comps):
		# Calculate impedance for specific number of components
		res = _lumped_network_helper(
			avail_vals,
			i,
			target,
			pre_calc,
			pre_calc_keys,
			pre_calc_depth,
			max_abs_error,
		)

		# Break if good enough
		if abs(res[-1] - target) < max_abs_error:
			break

	# Convert to expression tree and return
	return ExprTree(res[0])

def _lumped_network_helper(
		avail_vals,
		num_comps,
		target,
		pre_calc,
		pre_calc_keys,
		pre_calc_depth,
		max_error
	):

	# Intial values
	best_error = inf
	best_val   = None
	best_expr  = None

	# Find closest pre-calculated value and corresponding expression
	index = bisect(pre_calc_keys, target)
	try:
		# Update to pre-calculated data
		best_val   = pre_calc_keys[index]
		best_expr  = pre_calc[best_val]
		best_error = abs(target - best_val)
	except IndexError:
		pass
	try:
		# Get pre-calculated data
		val  = pre_calc_keys[index-1]
		expr = pre_calc[val]

		# Update if better
		if abs(target - val) < best_error:
			best_val   = val
			best_expr  = expr
			best_error = abs(target - best_val)
	except IndexError:
		pass

	# Return if everything is already calculated or if good enough
	if num_comps <= pre_calc_depth or best_error <= max_error:
		return (best_expr, best_val)

	# Include one additional impedance
	for val in avail_vals:
		# Return immediately if exact match
		if val == target:
			return [val], val

		# Recursively add series impedance if undershooting target
		elif val < target:
			# Needed series impedance to hit target
			needed = target - val

			# Recursive call
			expr, recursive_val = _lumped_network_helper(
				avail_vals,
				num_comps-1,
				needed,
				pre_calc,
				pre_calc_keys,
				pre_calc_depth,
				max_error,
			)

			# Update if better
			error = abs(needed - recursive_val)
			if error < best_error:
				best_error = error
				best_val   = recursive_val + val
				best_expr  = [_add, val, *expr]
				if best_error <= max_error:
					return best_expr, best_val

		# Recursively add parallel impedance if overshooting target
		else:
			# Needed parallel impedance to hit target
			needed = (val * target) / (val - target)

			# Recursive call
			expr, recursive_val = _lumped_network_helper(
				avail_vals,
				num_comps-1,
				needed, pre_calc,
				pre_calc_keys,
				pre_calc_depth,
				max_error,
			)

			# Update if better
			error = abs(needed - recursive_val)
			if error < best_error:
				best_error = error
				best_val   = (val * recursive_val) / (val + recursive_val)
				best_expr  = [parallel_impedance, val, *expr]
				if best_error <= max_error:
					return best_expr, best_val
	return best_expr, best_val

# def lumped_network(
# 		target,
# 		max_num_comps = inf,
# 		max_rel_error = None,
# 		max_abs_error = None,
# 		avail_vals    = get_avail_vals('E6'),
# 		avail_ops     = [parallel_impedance, _add],
# 	):
# 	"""
# 	Finds a network of passive components matching a specified (possibly complex) value.

# 	Args:
# 		target (number):        Target impedance for the network.

# 	Kwargs:
# 		max_num_comps (int):    Maximum number of components in the network. The function will return a network with no more components than this value.
# 		max_rel_error (number): (Default 0.01) Maximum tolerable relative error. The relative error of the resulting network will be less than this value if that is possible given 'max_num_comps'.
# 		max_abs_error (number): Maximum tolerable absolute error. The absolute error of the resulting network will be less than this value if that is possible given 'max_num_comps'.
# 		avail_vals ([number]):  List of available values of the impedances used in the network.
# 		avail_ops ([operator]): (Default: [eppp.calc.parallel_impedance, operator.add]) List of operators used for calculating the resulting impedance. The operators are represented by a function that takes to arguments. The operators must be associative and commutative.

# 	Returns:
# 		ExprTree. Expression tree of the resulting network. Use ExprTree.evaluate() to get it's value.
# 	"""

# 	# Make target real type if it is real
# 	if complex(target).imag == 0:
# 		target = complex(target).real

# 	# Check what types of numbers 'avail_vals' contains
# 	has_complex_vals = complex in map(type, avail_vals)
# 	if has_complex_vals:
# 		may_have_negative_vals = True
# 	else:
# 		may_have_negative_vals = True in map(lambda x: x < 0, avail_vals)

# 	# Sort 'avail_vals' if not complex
# 	if not has_complex_vals:
# 		avail_vals.sort()

# 	# Use more general parallel function if 'avail_vals' contains 0, infinity or negative values
# 	if 0 in avail_vals \
# 	or inf in avail_vals \
# 	or may_have_negative_vals:
# 		avail_ops = list(map(lambda x: parallel_impedance if x == _parallel_impedance_non_strict else x, avail_ops))

# 	# Use less general function otherwise
# 	else:
# 		avail_ops = list(map(lambda x: _parallel_impedance_non_strict if x == parallel_impedance else x, avail_ops))

# 	# Determine whether a strict polish_eval function must be used
# 	polish_eval_func = _polish_eval_non_strict
# 	for op in avail_ops:
# 		if  op != _add \
# 		and op != _parallel_impedance_non_strict:
# 			polish_eval_func = lambda x: _polish_eval(x)[0]

# 	# Don't display a unit (may change later)
# 	# unit = 'Ω'
# 	unit = ''

# 	# Check so that target is non-zero
# 	if target == 0:
# 		raise ValueError("Target impedance must be non-zero.")

# 	# Figure out error mode
# 	if max_abs_error is None and max_rel_error is None:
# 		max_error = 0.01
# 		use_rel_error = True
# 	elif not max_abs_error is None and not max_rel_error is None:
# 		raise ValueError("Can not specify both 'max_abs_error' and 'max_rel_error'.")
# 	elif not max_abs_error is None:
# 		max_error = max_abs_error
# 		use_rel_error = False
# 	else:
# 		max_error = max_rel_error
# 		use_rel_error = True

# 	# Initial values
# 	best_error = inf
# 	best_value = None
# 	best_expr  = None

# 	# Insertions generator
# 	def insertions_gen(ops, last_op = None):
# 		# Base case
# 		if len(ops) == 0:
# 			yield [-1]

# 		# Recurse
# 		else:
# 			cur_op = ops[0]
# 			for insertions in insertions_gen(ops[1:], last_op = cur_op):
# 				# Avoid redundant insertion variations by not varying operator order in case of consecutive equal operations
# 				if cur_op == last_op or cur_op == None:
# 					yield [2] + insertions

# 				# Non-redundant case
# 				else:
# 					yield [1] + insertions
# 					yield [2] + insertions

# 	# For all numbers of components, starting from one and up until return
# 	for num_comps in _it.count(1):
# 		_log(1, 'Finding lumped network for %i component%s...' % (num_comps, '' if num_comps == 1 else 's'))

# 		# Initialize stuff that can be known in advance for performance
# 		num_ops  = num_comps - 1
# 		expr_len = 2 * num_comps - 1
# 		expr     = [0] * expr_len

# 		# Precalculate lists of non-redundant combinations of operations
# 		ops_len             = 2 ** num_ops
# 		ops_range           = range(ops_len)
# 		insertions_pre_calc = [0] * ops_len
# 		ops_pre_calc        = [0] * ops_len
# 		index               = 0
# 		for ops in _it.product(avail_ops, repeat = num_ops):
# 			ops_pre_calc[index] = ops
# 			if num_comps == 1:
# 				insertions_pre_calc[index] = [[-1]]
# 			elif num_comps <= 2:
# 				insertions_pre_calc[index] = [[0, -1]]
# 			else:
# 				insertions_pre_calc[index] = []
# 				for insertions in insertions_gen(ops[1:], ops[0]):
# 					insertions_pre_calc[index].append([0] + insertions)
# 			index += 1

# 		# For all non-redundant combinations of values
# 		for values in _it.combinations_with_replacement(avail_vals, num_comps):
# 			# Do not calculate obvious sub-optimal values
# 			if not may_have_negative_vals:
# 				if sum(values) < target - best_error:
# 					continue
# 				# if parallel_impedance(*values) > target + best_error:
# 				# 	continue
# 				# Approximation (subset) of the above which is faster to calculate
# 				if values[0] > (target + best_error) * num_comps: # 'values[0]' = 'min(values)' since list is sorted
# 					continue

# 			# For all non-redundant combinations of operations
# 			for op_index in ops_range:
# 				# Use pre-calculated list of operations
# 				ops = ops_pre_calc[op_index]

# 				# Build expression from insertions
# 				for insertions in insertions_pre_calc[op_index]:
# 					if num_comps == 1:
# 						value   = values[0]
# 						expr[0] = value
# 					else:
# 						expr[0]   = ops[0]
# 						op_index  = 1
# 						val_index = 0
# 						index     = 1
# 						while op_index < num_ops:
# 							if insertions[op_index] == 2:
# 								expr[index] = values[val_index]
# 								val_index += 1
# 								index     += 1
# 							expr[index] = ops[op_index]
# 							op_index += 1
# 							index    += 1
# 						expr[index:] = values[val_index:]

# 						# Get value from evaluated expression
# 						value = polish_eval_func(expr)

# 					# Calculate error
# 					error = abs(value - target)

# 					# Remember result if best so far
# 					if error <= best_error:
# 						# Remember best things
# 						best_error = error
# 						best_value = value

# 						# Rebuild the expression
# 						best_expr  = [0] * expr_len
# 						insert_pos = insertions[0]
# 						op_index   = 0
# 						val_index  = 0
# 						index      = 0
# 						while index < expr_len:
# 							if index == insert_pos:
# 								best_expr[index] = ops[op_index]
# 								op_index   += 1
# 								insert_pos += insertions[op_index]
# 							else:
# 								best_expr[index] = values[val_index]
# 								val_index += 1
# 							index += 1

# 						# Return if an optimal solution has been found
# 						if best_error == 0:
# 							return ExprTree(best_expr, unit = unit)

# 		# Calculate error
# 		if use_rel_error:
# 			best_signed_error = (best_value - target) / abs(target) # Division-by-zero safe since target can't be 0
# 		else:
# 			best_signed_error = best_value - target

# 		# Log best error so far
# 		if use_rel_error:
# 			_log(2, 'Best relative error so far: %s' % (_str_sci(best_signed_error)))
# 		else:
# 			_log(2, 'Best absolute error so far: %s' % (_str_sci(best_signed_error)))

# 		# Log best network
# 		_log(3, 'Best network so far: '+ str(ExprTree(best_expr, unit = unit)))

# 		# Return if sufficiently good or maximum number of components have been used
# 		if abs(best_signed_error) <= max_error or num_comps == max_num_comps:
# 			return ExprTree(best_expr, unit = unit)
