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

import pylab           as _pl
import itertools       as _it
import inout           as _inout
import operator        as _op
from error import _stringOrException
from log import _log
from debug import *

class ExprTree:
	def __str__(self):
		if self._isLeaf():
			return _inout.strSci(self.data)
		else:
			operator = self.data[0]
			operands = self.data[1]
			
			# Use symbols for some functions
			symbolDict = {
				_op.add:     '+' ,
				parallelRes: '||',
			}
			opSym = symbolDict[operator] if operator in symbolDict else str(operator)
			
			# Form expression
			ret = ''
			for operand in operands[:-1]:
				ret += str(operand) +' '+ opSym +' '
			ret += str(operands[-1])
			
			return '('+ ret +')'
	
	def __init__(self, expr, preserveExpr = True, fmt = 'polish', doSimplify = True):
		# Do not modify expression unless explicitly stated
		if preserveExpr:
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
				self.data[1].append(ExprTree(expr, preserveExpr = False, fmt = 'reverse-polish'))
		else: # If leaf
			self.data = el
		
		# Simplify
		if doSimplify:
			self.simplify()
	
	def _isLeaf(self):
		return not isinstance(self.data, tuple)
	
	def _getSize(self):
		if self._isLeaf():
			return 1
		else:
			ret = 0
			for operand in self.data[1]:
				ret += operand._getSize()
			return ret
	
	def simplify(self):
		if not self._isLeaf():
			operator = self.data[0]
			operands = self.data[1]
			
			# Build new operands
			newOperands = []
			for operand in operands:
				# Simplify child
				operand.simplify()
				
				# Steal child's operands if it is of the same type of operand as this one
				if not operand._isLeaf() and operand.data[0] is operator:
					newOperands.extend(operand.data[1])
				
				# Add unmodified operand otherwise
				else:
					newOperands.append(operand)
			
			# Sort operands by size
			newOperands.sort(key = lambda x: x._getSize())
			
			# Update data
			self.data = (operator, newOperands)

def _polishEval(expr, stack = None):
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
			return (_polishEval(expr, stack))
		
		# If value
		else:
			stack.append(el)
			return _polishEval(expr, stack)

def parallelRes(*vals):
	ret = vals[0]
	for val in vals[1:]:
		if val == 0:
			return 0
		elif val == float('inf'):
			ret = val
		else:
			ret *= val / (val + ret)
	return ret

def getAvailVals(series = 'E6', minVal = 10, maxVal = 10000000, compType = 'resistor', freq = None):
	# Component type setting
	if not compType in ['resistor', 'capacitor', 'inductor']:
		raise Exception("'compType' must be either 'resistor', 'capacitor' or 'inductor'.")
	if compType in ['capacitor', 'inductor'] and freq == None:
		raise Exception("'freq' must be specified if '%s' is chosen as component type." % compType)
	
	# Dictionry with common series
	# TODO: Add more
	# TODO: Calculate these?
	availValsDict = {}
	availValsDict['E6']  = [10.,      15.,      22.,      33.,      47.,      68.     ]
	availValsDict['E12'] = [10., 12., 15., 18., 22., 27., 33., 39., 47., 56., 68., 82.]
	
	# Get basic available values
	if type(series) is str:
		basicAvailVals = availValsDict[series]
	else:
		basicAvailVals = series
	availVals = list(basicAvailVals)
	
	# Append higher order series
	multiplier = 10
	while availVals[-1] <= maxVal:
		availVals  += map(lambda x: x*multiplier, basicAvailVals)
		multiplier *= 10
	
	# Reverse for more efficient list operations
	availVals.reverse()
	basicAvailVals.reverse()
	
	# Append low order series
	divider = 10
	while availVals[-1] >= minVal:
		availVals += map(lambda x: x / divider, basicAvailVals)
		divider   *= 10
	
	# Reverse again for ordered list
	availVals.reverse()
	
	# Filter out too high or too low values
	availVals = filter(lambda x: x <= maxVal, availVals)
	availVals = filter(lambda x: x >= minVal, availVals)
	
	# Transform values according to the type of component type
	if compType == 'resistor':
		compSpecificFunc = lambda x: x
	elif compType == 'capacitor':
		compSpecificFunc = lambda x: 1/(1j * x * freq)
	elif compType == 'inductor':
		compSpecificFunc = lambda x: 1j * x * freq
	availVals = map(compSpecificFunc, availVals)
	
	return list(availVals)

def lumpedNetwork(
		target,
		maxNumComps = float('inf'),
		maxRelError = None,
		maxAbsError = None,
		availVals = getAvailVals('E6'),
		availOps = [parallelRes, _op.add]
	):
	'''
	Finds a network of passive components matching a specified (possibly complex) value.
	
	Args:
		target (number):       Target impedance for the network
	
	Kwargs:
		maxNumComps (int):    Maximum number of components in the network. The function will return a network with no more components than this value.
		maxRelError (number): Maximum tolerable relative error. The function will return a network with at most this value as relative error if possible with the given 'maxNumComps'.
		maxAbsError (number): Maximum tolerable absolute error. The function will return a network with at most this value as absolute error if possible with the given 'maxNumComps'. This argument should not be given if 'maxRelError' is given.
		availVals ([number]): List of available values of the impedances used in the network
	
	Returns:
		[...]. Polish expression of the resulting network. (Use TODO functions to get something useful)
	'''
	
	# Check so that target is non-zero
	if target == 0:
		return _stringOrException("Target impedance must be non-zero.")
	
	# Figure out error mode
	if maxAbsError is None and maxRelError is None:
		maxError = 0
		useRelError = True
	elif not maxAbsError is None and not maxRelError is None:
		return _stringOrException("Can not specify both 'maxAbsError' and 'maxRelError'.")
	elif not maxAbsError is None:
		maxError = maxAbsError
		useRelError = False
	else:
		maxError = maxRelError
		useRelError = True
	
	# Initial values
	bestError = float('inf')
	bestExpr  = None
	
	# For all numbers of components, starting from one up to 'maxNumComps'
	for numComps in _it.count(1):
		_log(1, 'Finding lumped network for %i component%s...' % (numComps, '' if numComps == 1 else 's'))
		
		# Insertions generator
		def insertionsGen(ops, lastOp = None):
			# Base case
			if len(ops) == 0:
				yield []
			
			# Recurse
			else:
				curOp = ops[0]
				for insertions in insertionsGen(ops[1:], lastOp = curOp):
					# Avoid redundant insertion variations by not varying operator order in case of consecutive equal operations
					if curOp == lastOp or curOp == None:
						yield [1] + insertions
					
					# Non-redundant case
					else:
						yield [0] + insertions
						yield [1] + insertions
		
		bestSignedError = None
		for values in _it.combinations_with_replacement(availVals, numComps):
			for ops in _it.product(availOps, repeat = numComps - 1):
				for insertions in insertionsGen(ops):
					# Initilize expression and insert position
					expr = list(values)
					insertPos = 0
					
					# Insert functions in expression in every valid way except in redundant ways
					opList = list(ops)
					for insertion in insertions:
						expr.insert(insertPos, opList.pop())
						insertPos += insertion + 1
					
					# Get value from evaluated expression
					value = _polishEval(expr)[0]
					
					# Calculate error
					if useRelError:
						error = abs((value - target) / target) # Division-by-zero safe since target can not be 0
					else:
						error = abs(value - target)
					
					# Remember result if best so far
					if error <= bestError:
						bestError = error
						bestExpr  = expr
						bestSignedError = bestError * _pl.sign(value - target)
						
						# Return if an optimal solution has been found
						if bestError == 0:
							return ExprTree(bestExpr)
		
		# Log best error so far
		if bestSignedError is not None:
			if useRelError:
				_log(2, 'Best relative error so far: %s' % (_inout.strSci(bestSignedError*100, '%')))
			else:
				_log(2, 'Best absolute error so far: %s' % (_inout.strSci(bestSignedError)))
		
		# Log best network
		_log(3, 'Best network so far: '+ str(ExprTree(bestExpr)))
		
		# Return if sufficiently good or maximum number of components have been used
		if bestError <= maxError or numComps == maxNumComps:
			return ExprTree(bestExpr)
