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
from bisect import bisect, insort
from math   import inf, nan

# Internal
from .debug import *
from .inout import str_sci as _str_sci
from .log   import _log

#=======
# Other
#=======

# String representation for functions decorator
def func_sym_rep(sym_rep):
	def decorator(func):
		func.sym_rep = sym_rep
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
			# Use symbol representation if available
			op_sym = self.operator.sym_rep if hasattr(self.operator, 'sym_rep') else str(self.operator)

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

def inductor_impedance(ind, freq):
	"""
	Calculates the impedance of an inductor for a given frequency.

	Args:
		ind (number):  Inductance [H]
		freq (number): Frequency  [Hz]

	Returns:
		The impedance for an inductor with the specified inductance at the specified frequency.
	"""
	return ind * 1j * 2 * _np.pi * freq

def capacitor_impedance(cap, freq):
	"""
	Calculates the impedance of capacitor for a given frequency.

	Args:
		cap (number):  Capacitance [F]
		freq (number): Frequency   [Hz]

	Returns:
		The impedance for a capacitor with the specified capacitance at the specified frequency.
	"""

	if cap == 0 or freq == 0:
		return -1j * inf
	else:
		return 1 / (cap * 1j * 2 * _np.pi * freq)

def inductor_admittance(ind, freq):
	"""
	Calculates the admittance of an inductor for a given frequency.

	Args:
		ind (number):  Inductance [H]
		freq (number): Frequency  [Hz]

	Returns:
		The admittance for an inductor with the specified inductance at the specified frequency.
	"""
	if ind == 0 or freq == 0:
		return -1j * inf
	else:
		return 1 / (ind * 1j * 2 * _np.pi * freq)

def capacitor_admittance(cap, freq):
	"""
	Calculates the admittance of capacitor for a given frequency.

	Args:
		cap (number):  Capacitance [F]
		freq (number): Frequency   [Hz]

	Returns:
		The admittance for a capacitor with the specified capacitance at the specified frequency.
	"""

	return cap * 1j * 2 * _np.pi * freq

def voltage_division(voltage, imp_main, *imps):
	"""
	Calculates the voltage divided over series connected impedances.

	Args:
		voltage (number):  Source voltage. [V]
		imp_main (number): Main impedance. [Ω]
		*imps (number):    Other series connected impedances. [Ω]

	Returns:
		The voltage arising over 'imp_main' when 'imp_main' is connected in series with 'imps' with 'voltage' volts over them. [V]
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

def current_division(current, imp_main, *imps):
	"""
	Calculates the current divided over parallel connected impedances.

	Args:
		voltage (number):  Source current. [A]
		imp_main (number): Main impedance. [Ω]
		*imps (number):    Other parallel connected impedances. [A]

	Returns:
		The current passing through 'imp_main' when 'imp_main' is connected in parallel with 'imps' with 'current' amperes entering the network. [A]
	"""

	# Equivalent impedance of non-main impedances
	imp_others = parallel_impedance(*imps)

	if abs(imp_others) == inf:
		if abs(imp_main) == inf:
			return nan
		else:
			return _np.sign(imp_main) * current

	try:
		return current * imp_others / (imp_main + imp_others)

	except ZeroDivisionError:
		if current * imp_others == 0:
			return nan
		else:
			return _np.sign(current * imp_others) * inf

@func_sym_rep('||')
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

# Same as 'parallel_impedance', but only takes 2 arguments and assumes non-zero, finite impedances and is thus faster
@func_sym_rep('||')
def _parallel_impedance_non_strict(z1, z2):
	return z1*z2 / (z1 + z2)

# Sums two numbers (for series impedance calculations)
@func_sym_rep('+')
def _add(x1, x2):
	return x1 + x2

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
	expr = expr.replace('^', '**')  # Use '^' for exponentiation

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

# Same as '_polish_eval' but with these differences:
# - Assumes complete evaluation to exactly one element
# - Does not preserve 'expr'
# - Assumes the only functions are '_parallel_impedance_non_strict' and '_add'
# - Extra argument for pre-calculated list length
# def polish_eval_non_strict(expr):

# Import and initialize C version of '_polish_eval_non_strict'
try:
	from .fast_misc import polish_eval_non_strict      as _polish_eval_non_strict
	from .fast_misc import polish_eval_non_strict_init as _polish_eval_non_strict_init
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

def make_resistance(
		target,
		max_num_comps             = -1,
		tolerance                 = 0.01,
		avail_vals                = get_avail_vals('E6'),
		avail_ops                 = None, # TODO: Not used; Remove or rework
		num_comps_full_search     = 3,
		num_comps_full_search_lag = 3,
	):
	"""
	Finds a network of resistances approximating a target value.

	Args:
		target (number): Target resistance for the network.

	Kwargs:
		max_num_comps (int):             Maximum number of components in the network. The function will return a network with no more components than this value. A negative value sets the limit to infinity.
		tolerance (float):               (Default 0.01) Maximum tolerable relative error. The relative error of the resulting network will be less than this value if that is possible given 'max_num_comps'.
		avail_vals ([float]):            (Default: get_avail_vals('E6')) List of available values of the resistances used in the network.
		avail_ops ([operator]):          (Default: [eppp.calc.parallel_impedance, operator.add]) List of operators used for calculating the resulting resistance. The operators are represented by a function that takes two arguments. The operators must be associative and commutative.
		num_comps_full_search (int):     (Default: 3) Maximum number of components to do a full search on. Affects performance only. A higher value consumes more memory but may be faster.
		num_comps_full_search_lag (int): (Default: 3) How many components should be search for before starting with the full searches. Affects performance only. A higher value increases performance for small number of components with the trade-off that the performance for large number of components is slightly reduced (assuming that 'num_comps_full_search' is configured for a efficient searches).

	Returns:
		ExprTree. Expression tree of the resulting network. Use ExprTree.evaluate() to get it's value.
	"""

	# Dynamic programming dictionary
	results = {}

	# Results for single component
	for val in avail_vals:
		results[val] = [val]
	results_keyss = [sorted(results.keys())]

	# Loop up to maximum number of components
	for num_comps in _it.count(1) if max_num_comps <= 0 else range(1, max_num_comps+1):
		# Extend results keys list
		if num_comps > 1:
			results_keyss.append([])

		# Fully search for lower number of components
		num_comps_fully_searched = num_comps - num_comps_full_search_lag
		if 1 < num_comps_fully_searched <= num_comps_full_search:
			for val in avail_vals:
				for old_val in results_keyss[num_comps_fully_searched-1-1]:
					expr = results[old_val]

					# Store series result
					new_val = val + old_val
					if not new_val in results:
						results[new_val] = [_add, val, *expr]
						insort(results_keyss[num_comps_fully_searched-1], new_val)

					# Store parallel result
					new_val = (val * old_val) / (val + old_val)
					if not new_val in results:
						results[new_val] = [parallel_impedance, val, *expr]
						insort(results_keyss[num_comps_fully_searched-1], new_val)

		# When not doing more full searches, limit 'num_comps_fully_searched'
		num_comps_fully_searched = min(num_comps_fully_searched, num_comps_full_search)

		# Calculate resistance for specific number of components
		res = _make_resistance_helper(
			avail_vals,
			target,
			num_comps,
			max(num_comps_fully_searched, 1),
			tolerance,
			results,
			results_keyss,
		)

		# Break if good enough
		if abs(target - res[-1]) <= tolerance * target:
			break

	# Convert to expression tree and return
	return ExprTree(res[0])

def _make_resistance_helper(
		avail_vals,
		target,
		num_comps,
		num_comps_fully_searched,
		tolerance,
		results,
		results_keyss,
	):

	# Intial values
	best_error = inf
	best_val   = None
	best_expr  = None

	# Find closest pre-calculated value and corresponding expression
	for results_keys in results_keyss[:num_comps]:
		index = bisect(results_keys, target)
		try:
			# Get pre-calculated results
			val  = results_keys[index]
			expr = results[val]

			# Update if better
			if abs(target - val) < best_error:
				best_val   = val
				best_expr  = results[best_val]
				best_error = abs(target - best_val)
		except IndexError:
			pass
		try:
			# Get pre-calculated results
			val  = results_keys[index-1]
			expr = results[val]

			# Update if better
			if abs(target - val) < best_error:
				best_val   = val
				best_expr  = expr
				best_error = abs(target - best_val)
		except IndexError:
			pass

		# Return if only one component or if the search is full
		if num_comps == 1 or num_comps <= num_comps_fully_searched:
			return best_expr, best_val

	# Include an additional resistance
	for val in avail_vals:
		# Recursively add series resistance if undershooting target
		if val < target:
			# Needed series resistance to hit target
			needed = target - val

			# Recursive call
			rec_expr, rec_val = _make_resistance_helper(
				avail_vals,
				needed,
				num_comps-1,
				num_comps_fully_searched,
				tolerance, # TODO: New tolerance?
				results,
				results_keyss,
			)
			new_expr = [_add, val, *rec_expr]
			new_val  = rec_val + val

			# Save new expression if truly new
			if not new_val in results:
				results[new_val] = new_expr
				new_num_comps = len(new_expr) // 2 + 1
				insort(results_keyss[new_num_comps-1], new_val)

			# Update if better
			error = abs(target - new_val)
			if error < best_error:
				best_error = error
				best_val   = new_val
				best_expr  = new_expr

		# Recursively add parallel resistance if overshooting target
		else:
			# Needed parallel resistance to hit target
			needed = (val * target) / (val - target)

			# Recursive call
			rec_expr, rec_val = _make_resistance_helper(
				avail_vals,
				needed,
				num_comps-1,
				num_comps_fully_searched,
				tolerance, # TODO: New tolerance?
				results,
				results_keyss,
			)
			new_expr = [parallel_impedance, val, *rec_expr]
			new_val  = rec_val * val / (rec_val + val)

			# Save new expression if truly new
			if not new_val in results:
				results[new_val] = new_expr
				new_num_comps = len(new_expr) // 2 + 1
				insort(results_keyss[new_num_comps-1], new_val)

			# Update if better
			error = abs(target - new_val)
			if error < best_error:
				best_error = error
				best_val   = new_val
				best_expr  = new_expr

	return best_expr, best_val
