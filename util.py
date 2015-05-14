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
	return res1 * res2 / (res1 + res2)

def _seriesRes(res1, res2):
	res1 = float(res1)
	res2 = float(res2)
	return res1 + res2

# TODO: Custom series
# TODO: Loop for smaller values also
def _getAvailVals(series = 'E6', minVal = 10, maxVal = 10000000):
	# Dictionry with common series
	availValsDict = {}
	availValsDict['E6']  = [10.,      15.,      22.,      33.,      47.,      68.     ]
	availValsDict['E12'] = [10., 12., 15., 18., 22., 27., 33., 39., 47., 56., 68., 82.]
	
	# Generate higher order series
	basicAvailVals = availValsDict[series]
	availVals = list(basicAvailVals)
	multiplier = 10
	while availVals[-1] <= maxVal:
		availVals += map(lambda x: x*multiplier, basicAvailVals)
		multiplier *= 10
	availVals = filter(lambda x: x <= maxVal, availVals)
	availVals = filter(lambda x: x >= minVal, availVals)
	availVals += [0]
	
	return availVals

import itertools as _it

# def findResitorNetwork(target, availVals = _getAvailVals('E6'), availOps = [_parallelRes, _seriesRes], maxError = 0.01):

def bestResistorNetwork(target, numComps, availVals = _getAvailVals('E6'), availOps = [_parallelRes, _seriesRes]):
	bestError = float('inf')
	bestCombination = None
	
	# TODO: Comment
	# TODO: This can probably be done without almost exclusively producing invalid expressions
	combinations = _it.product(availVals + availOps, repeat = 2*numComps - 1)
	for combination in combinations:
		try:
			combination = list(combination)  # Listify
			evald = _polishEval(combination) # Evaluate expression polishly
			
			# Check that expression is completely evaluated
			if len(evald) != 1:
				raise Exception('Expression is not completely evaluated.')
			
			value = evald[0]            # Get value from evaluated expression
			error = abs(target - value) # Calculate error
			
			# Remember result if best so far
			if error < bestError:
				bestError = error
				bestCombination = combination
		
		# Throw away all exceptions
		except:
			pass
		
	return bestCombination

# TODO: Remove
# Test

bc = bestResistorNetwork(68812, 2)
print bc
print _polishEval(bc)

# print _polishEval([4])
# print _polishEval([_parallelRes, 4, 4])
# print
# print _polishEval([_seriesRes, 4, _parallelRes, 4, 8])

