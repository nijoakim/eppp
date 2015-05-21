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
		if callable(el):
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
	
	return list(availVals)

def findResistorNetwork(target, availVals = _getAvailVals('E6'), availOps = [_parallelRes, _seriesRes], maxRelError = 0.01):
	relError = float('inf')
	numComps = 1
	expr = None
	while abs(relError) > maxRelError:
		print('Trying with %i components...' % numComps) # TODO: Log with log.py (level 1)
		expr  = bestResistorNetwork(target, maxNumComps = numComps, availVals = availVals, availOps = availOps, recurse = False)
		if expr is None:
			printVar(target)
			printVar(numComps)
			printVar(availOps)
			raise Exception()
		value = _polishEval(expr)[0]
		relError = (target - value) / target
		print('Best relative error so far: %f %%' % (100*relError)) # TODO: Log with log.py (level 2) $ TODO: Print with standard significant digits
		numComps += 1
	return expr

# TODO: Combine this and the above function into one function
def findNetwork(target, maxNumComps = float('inf'), maxError = 0, availVals = _getAvailVals('E6'), availOps = [_parallelRes, _seriesRes]):
	bestError = float('inf')
	bestExpr  = None
	
	# For all numbers of components, starting from one up to 'maxNumComps'
	for numComps in _it.count(1):
		printVar(numComps)
		# For every combination of non-equivalent connections
		DEBUG_count = 0
		for values in _it.combinations_with_replacement(availVals, numComps):
			for ops in _it.product(availOps, repeat = numComps - 1):
				# Insertions generator
				def insertionsGen(ops, lastOp = None):
					# Base case
					if len(ops) == 0:
						yield []
					
					# Recurse
					else:
						curOp = ops[0]
						for insertions in insertionsGen(ops[1:], lastOp = curOp):
							# Avoid redundant insertion variations by not varying operator order in case of two consecutive equal operations
							if curOp == lastOp or curOp == None:
								yield [1] + insertions
							
							# Non-redundant case
							else:
								yield [0] + insertions
								yield [1] + insertions
				
				for insertions in insertionsGen(ops):
					# Initilize expression and insert position
					expr = list(values)
					insertPos = 0
					
					# Insert functions in expression in every valid way except in redundant ways
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
					
					DEBUG_count += 1
	
		# TODO: Logging
		if bestError <= maxError or numComps == maxNumComps:
			printVar(DEBUG_count)
			return bestExpr



# TODO: Remove
# Test
import time
t = time.time()
# bc = bestResistorNetwork(12345, 4, availVals = _getAvailVals('E6', minVal = 10))
bc = findNetwork(88123, availVals = _getAvailVals('E6', minVal = 10), maxError = 100)
# bc = findResistorNetwork(525, availVals = [1000, 500, 50], maxRelError = 0)
_dbg.printVar(time.time() - t, 'time')
print(bc)
print(_polishEval(bc))
