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

import debug as _dbg
import itertools as _it

printVar = _dbg.printVar

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
		if hasattr(el, '__call__'):
			expr.append(el(stack.pop(), stack.pop()))
			return (_polishEval(expr, stack))
			
		# If value
		else:
			stack.append(el)
			return _polishEval(expr, stack)

def _parallelRes(res1, res2):
	res1 = float(res1)
	res2 = float(res2)
	if res1 == 0 and res2 == 0:
		return 0
	else:
		return res1 * res2 / (res1 + res2)

def _seriesRes(res1, res2):
	res1 = float(res1)
	res2 = float(res2)
	return res1 + res2

def _getAvailVals(series = 'E6', minVal = 10, maxVal = 10000000):
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
	
	return availVals

def findResistorNetwork(target, availVals = _getAvailVals('E6'), availOps = [_parallelRes, _seriesRes], maxRelError = 0.01):
	relError = float('inf')
	numComps = 1
	expr = None
	while abs(relError) > maxRelError:
		print('Trying with %i components...' % numComps) # TODO: Log with log.py (level 1)
		expr  = bestResistorNetwork(target, maxNumComps = numComps, availVals = availVals, availOps = availOps, recurse = False)
		value = _polishEval(expr)[0]
		relError = (target - value) / target
		print('Best relative error so far: %f %%' % (100*relError)) # TODO: Log with log.py (level 2) $ TODO: Print with standard significant digits
		numComps += 1
	return expr

def bestResistorNetwork(target, maxNumComps, availVals = _getAvailVals('E6'), availOps = [_parallelRes, _seriesRes], recurse = True):
	bestError = float('inf')
	bestExpr  = None
	
	# Base case
	if maxNumComps == 0:
		return None
	
	# Find expressions of lower number of components if recursion is enabled
	elif recurse:
		bestExpr = bestResistorNetwork(target, maxNumComps - 1, availVals, availOps)
		
		# Update best error
		if not bestExpr is None:
			bestError = abs(target - _polishEval(bestExpr)[0])
	
	# For every combination
	for values in _it.combinations_with_replacement(availVals, maxNumComps):
		for ops in _it.product(availOps, repeat = maxNumComps - 1):
			for insertions in _it.product([0, 1], repeat = maxNumComps - 1):
				# Initilize expression and insert position
				expr = list(values)
				insertPos = 0
				
				# TODO: This method produces redundant expressions... Can it be improved?
				# Insert functions in expression in every valid way
				for insertion in insertions:
					opList = list(ops)
					expr.insert(insertPos, opList.pop())
					insertPos += insertion + 1
				
				value = _polishEval(expr)[0] # Get value from evaluated expression
				error = abs(target - value)  # Calculate error
				
				# Remember result if best so far
				if error <= bestError:
					bestError = error
					bestExpr = expr
	
	# TODO: Logging
	
	return bestExpr

# TODO: Remove
# Test
import time
t = time.time()
# bc = bestResistorNetwork(13, 3, availVals = _getAvailVals('E6', minVal = 10))
bc = findResistorNetwork(88123, availVals = _getAvailVals('E6', minVal = 10), maxRelError = 0.001005)
_dbg.printVar(time.time() - t, 'time')
print bc
print _polishEval(bc)
