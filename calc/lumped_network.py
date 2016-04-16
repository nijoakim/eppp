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
import pylab     as _pl
import itertools as _it
import operator  as _op

# Internal
from ..error import _string_or_exception
from ..log import _log
from ..debug import *
from ..inout import str_sci as _str_sci

#=======
# Other
#=======

class ExprTree:
	def __str__(self):
		if self._is_leaf():
			return _str_sci(self.data)
		else:
			operator = self.data[0]
			operands = self.data[1]
			
			# Use symbols for some functions
			symbol_dict = {
				_op.add:      '+' ,
				parallel_imp: '||',
			}
			op_sym = symbol_dict[operator] if operator in symbol_dict else str(operator)
			
			# Form expression
			ret = ''
			for operand in operands[:-1]:
				ret += str(operand) +' '+ op_sym +' '
			ret += str(operands[-1])
			
			return '('+ ret +')'
	
	def __init__(
			self,
			expr,
			preserve_expr = True,
			fmt           = 'polish',
			do_simplify   = True
		):
		# Do not modify expression unless explicitly stated
		if preserve_expr:
			expr = list(expr)
		
		# Check so that a valid expression format has been given
		if fmt == 'polish':
			expr.reverse()
		elif fmt == 'reverse-polish':
			pass
		else:
			raise Exception('Invalid format.')
		
		# Consume polishly
		el = expr.pop()
		if callable(el): # If not leaf
			self.data = (el, [])
			for i in range(2): # Do twice
				self.data[1].append(ExprTree(expr, preserve_expr = False, fmt = 'reverse-polish'))
		else: # If leaf
			self.data = el
		
		# Simplify
		if do_simplify:
			self.simplify()
	
	def _is_leaf(self):
		return not isinstance(self.data, tuple)
	
	def _getSize(self):
		if self._is_leaf():
			return 1
		else:
			ret = 0
			for operand in self.data[1]:
				ret += operand._getSize()
			return ret
	
	def simplify(self):
		if not self._is_leaf():
			operator = self.data[0]
			operands = self.data[1]
			
			# Build new operands
			new_operands = []
			for operand in operands:
				# Simplify child
				operand.simplify()
				
				# Steal child's operands if it is of the same type of operand as this one
				if not operand._is_leaf() and operand.data[0] is operator:
					new_operands.extend(operand.data[1])
				
				# Add unmodified operand otherwise
				else:
					new_operands.append(operand)
			
			# Sort operands by size
			new_operands.sort(key = lambda x: x._getSize())
			
			# Update data
			self.data = (operator, new_operands)

def _polish_eval(expr, stack = None):
	# Do not modify original expression
	expr = list(expr)
	
	# Default empty stack
	if stack == None:
		stack = []
	
	# If empty expression
	if not expr:
		stack.reverse()
		return stack
	
	# If not empty expression
	else:
		el = expr.pop()
		
		# If operator (function)
		if callable(el):
			expr.append(el(stack.pop(), stack.pop()))
			return (_polish_eval(expr, stack))
		
		# If value
		else:
			stack.append(el)
			return _polish_eval(expr, stack)

def parallel_imp(*vals):
	"""
	Calculates the equivalent impedance of a set of parallel connected components.
	
	Args:
		*vals (number): Parallel impedances.
	
	Returns:
		The equivalent impedance for all '*vals' impedances connected in parallel.
	"""
	ret = vals[0]
	for val in vals[1:]:
		if val == 0:
			return 0
		elif val == float('inf'):
			ret = val
		else:
			ret *= val / (val + ret)
	return ret

def get_avail_vals(series = 'E6', min_val = 10, max_val = 10000000, comp_type = 'resistor', freq = None):
	# Component type setting
	if not comp_type in ['resistor', 'capacitor', 'inductor']:
		raise Exception("'comp_type' must be either 'resistor', 'capacitor' or 'inductor'.")
	if comp_type in ['capacitor', 'inductor'] and freq == None:
		raise Exception("'freq' must be specified if '%s' is chosen as component type." % comp_type)
	
	# Dictionry with common series
	# TODO: Add more
	# TODO: Calculate these?
	avail_vals_dict = {}
	avail_vals_dict['E6']  = [10.,      15.,      22.,      33.,      47.,      68.     ]
	avail_vals_dict['E12'] = [10., 12., 15., 18., 22., 27., 33., 39., 47., 56., 68., 82.]
	
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
	
	# Append low order series
	divider = 10
	while avail_vals[-1] >= min_val:
		avail_vals += map(lambda x: x / divider, basic_avail_vals)
		divider   *= 10
	
	# Reverse again for ordered list
	avail_vals.reverse()
	
	# Filter out too high or too low values
	avail_vals = filter(lambda x: x <= max_val, avail_vals)
	avail_vals = filter(lambda x: x >= min_val, avail_vals)
	
	# Transform values according to the type of component type
	if comp_type == 'resistor':
		comp_specific_func = lambda x: x
	elif comp_type == 'capacitor':
		comp_specific_func = lambda x: 1/(1j * x * freq)
	elif comp_type == 'inductor':
		comp_specific_func = lambda x: 1j * x * freq
	avail_vals = map(comp_specific_func, avail_vals)
	
	return list(avail_vals)

def lumped_network(
		target,
		max_num_comps = float('inf'),
		max_rel_error = None,
		max_abs_error = None,
		avail_vals    = get_avail_vals('E6'),
		avail_ops     = [parallel_imp, _op.add]
	):
	"""
	Finds a network of passive components matching a specified (possibly complex) value.
	
	Args:
		target (number):        Target impedance for the network
	
	Kwargs:
		max_num_comps (int):    Maximum number of components in the network. The function will return a network with no more components than this value.
		max_rel_error (number): Maximum tolerable relative error. The function will return a network with at most this value as relative error if possible with the given 'max_num_comps'.
		max_abs_error (number): Maximum tolerable absolute error. The function will return a network with at most this value as absolute error if possible with the given 'max_num_comps'. This argument should not be given if 'max_rel_error' is given.
		avail_vals ([number]):  List of available values of the impedances used in the network
	
	Returns:
		[...]. Polish expression of the resulting network. (Use <slafs> functions to get something useful)
	""" # TODO:  Replace slafs
	
	# Check so that target is non-zero
	if target == 0:
		return _string_or_exception("Target impedance must be non-zero.")
	
	# Figure out error mode
	if max_abs_error is None and max_rel_error is None:
		max_error = 0
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
					value = _polish_eval(expr)[0]
					
					# Calculate error
					if use_rel_error:
						error = abs((value - target) / target) # Division-by-zero safe since target can not be 0
					else:
						error = abs(value - target)
					
					# Remember result if best so far
					if error <= best_error:
						best_error = error
						best_expr  = expr
						best_signed_error = best_error * _pl.sign(value - target)
						
						# Return if an optimal solution has been found
						if best_error == 0:
							return ExprTree(best_expr)
		
		# Log best error so far
		if best_signed_error is not None:
			if use_rel_error:
				_log(2, 'Best relative error so far: %s' % (_str_sci(best_signed_error*100, '%')))
			else:
				_log(2, 'Best absolute error so far: %s' % (_str_sci(best_signed_error)))
		
		# Log best network
		_log(3, 'Best network so far: '+ str(ExprTree(best_expr)))
		
		# Return if sufficiently good or maximum number of components have been used
		if best_error <= max_error or num_comps == max_num_comps:
			return ExprTree(best_expr)
