# Copyright 2014-2015 Joakim Nilsson
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

# TODO: Document errors.
# TODO: Array length error checks.

import pylab as _pl
from error import _stringOrException

#=====================
# Decibel conversions
#=====================

def dB(x, power = False, inv = False):
	'''
	Converts a number to and from its decibel form.
	
	Args:
		x: number to be converted
	
	Kwargs:
		power (bool): Whether to use the power decibel definition. If False, the amplitude decibel definition is used instead.
		inv (bool):   Whether to convert from decibels instead of to. If False, the conversion is done to decibels, otherwise from.
	
	Returns:
		The converted form of 'x'.
	'''
	
	# Power decibels or not
	if power:
		factor = 10.
	else:
		factor = 20.
	
	# Convert
	if inv:
		return 10 ** (x/factor)
	else:
		return factor*_pl.log10(x)

#===========
# Bandwidth
#===========

def _breakFreq(freq, mag, di, decibel = 3, bandstop = False):
	# Size check
	if freq.size != mag.size:
		return _stringOrException("'freq' and 'mag' must be of the same size.")
	
	# Return negated if bandstop filter
	if bandstop:
		return _breakFreq(freq, -mag, di, decibel = decibel, bandstop = False)
	
	# Find out peak and break magnitude
	peakIndex = mag.argmax()
	breakMag = mag[peakIndex]*dB(-decibel, inv = True)
	
	# Search
	i = peakIndex
	while 0 <= i < mag.size:
		if mag[i] < breakMag:
			return freq[i]
		i += di
	
	# Out of bounds
	if i < 0:
		return 0.
	elif i >= mag.size:
		return _stringOrException("High break frequency is not in interval") # TODO: Only high?

def loBreakFreq(freq, mag, decibel = 3, bandstop = False):
	return _breakFreq(freq, mag, -1, decibel, bandstop)

def hiBreakFreq(freq, mag, decibel = 3, bandstop = False):
	return _breakFreq(freq, mag, 1, decibel, bandstop)

def bandwidth(freq, mag, decibel = 3, bandstop = False):
	return hiBreakFreq(freq, mag, decibel, bandstop) - loBreakFreq(freq, mag, decibel, bandstop)

# Dynamic docstring generation
def _docBandwidth(whatStr):
	return '''
		Calculates the %s of a filter.
		
		Args:
			freq (numpy.ndarray): Frequency data
			mag (numpy.ndarray):  Magnitude data
		
		Kwargs:
			decibel (number): Deviation from min/max value required to qualify as break frequency, given in amplitude decibels
			bandstop (bool):  Whether to treat data as a stop filter. If False, data is treated as a pass filter
		
		Returns:
			float. %s
	''' % (whatStr, whatStr[0].upper() + whatStr[1:])
loBreakFreq.__doc__ = _docBandwidth("low break frequency")
hiBreakFreq.__doc__ = _docBandwidth("high break frequency")
bandwidth.__doc__   = _docBandwidth("bandwidth")

#=========
# Margins
#=========

def intersects(x, y, target):
	'''
	Calculates where y = f(x) intersecsts target.
	
	Args:
		x (numpy.ndarray): x data
		y (numpy.ndarray): y data
		target (number):   y value for where the intersect is taken.
	
	Returns:
		float. x value for where y intersects target
	
	'''
	
	# Offset to zero for simplicity
	if target != 0:
		return intersects(x, y - target, 0)
	
	# Negate if below zero, return first if already intersets
	if y[0] < 0:
		return intersects(x, -y, 0)
	elif y[0] == 0:
		return x[0]
	
	# Search and return if found
	i = 0
	for el in y:
		if el < 0:
			# Return linear interpolation
			# y[i] - y[i-1] will never be zero because of previous checks
			# x[i-1] or y[i-1] will never be out of range because of previous checks
			slope = -(x[i] - x[i-1]) / (y[i] - y[i-1])
			return x[i-1] + slope * y[i-1]
		i += 1
	
	# Never reached target
	return _stringOrException("Data never intersects target.")

def unityGainFreq(freq, mag):
	'''
	Calculates unity gain frequency from magnitude data as function of frequency.
	
	Args:
		freq (numpy.ndarray): Frequency data
		mag (numpy.ndarray):  Magnitude data
	
	Returns:
		float. Unity gain frequency
	'''
	return intersects(freq, mag, 1)

def phase180Freq(freq, phase):
	'''
	Calculates frequency of 180 degree phase shift from magnitude data as function of frequency.
	
	Args:
		freq (numpy.ndarray):  Frequency data
		phase (numpy.ndarray): Phase data
	
	Returns:
		float. Frequency of 180 degrees phase shift
	'''
	
	freqs = []
	
	# Loop through all necessary phase 360-offsets
	for phaseOffset in range( (int(_pl.floor(min(phase))) / 360) * 360, (int(_pl.ceil(max(phase))) / 360) * 360, 360):
		# Error means no intersection for given phase and can therefore be ignored
		try:
			freqs.append(intersects(freq, phase - phaseOffset, 180))
		except:
			pass
	
	if freqs:
		# First intersection is the important one
		return min(freqs)
	else:
		# There were no 180 frequency
		return Exception("Phase never intersects 180 + 360*n.")

def gainMargin(freq, mag, phase, power = False):
	'''
	Calculates gain margin from magnitude and phase data, both as functions of frequency.
	
	Args:
		freq (numpy.ndarray):  Frequency data
		mag (numpy.ndarray):   Magnitude data
		phase (numpy.ndarray): Phase data
		power (bool):          Whether to use the power decibel definition. If False, the amplitude decibel definition is used instead.
	
	Returns:
		float. Gain margin in decibel
	'''
	return -dB(mag[abs(freq - phase180Freq(freq, phase)).argmin()], power = power)

def phaseMargin(freq, mag, phase):
	'''
	Calculates phase margin from magnitude and phase data, both as functions of frequency.
	
	Args:
		freq (numpy.ndarray):  Frequency data
		mag (numpy.ndarray):   Magnitude data
		phase (numpy.ndarray): Phase data
	
	Returns:
		float. Phase margin
	'''
	return 180 + phase[abs(freq - unityGainFreq(freq, mag)).argmin()]
