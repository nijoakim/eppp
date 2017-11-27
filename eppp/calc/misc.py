# Copyright 2014-2017 Joakim Nilsson
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

#=========
# Imports
#=========

# External
import numpy as _np

#=====================
# Decibel conversions
#=====================

# Docstring decorator for 'convert_to_db' and 'convert_from_db'.
def _doc_convert_db(convert_str):
	def decorator(func):
		func.__doc__ = """
			Converts a number to and from its decibel form.

			Args:
				x: number to be converted.

			Kwargs:
				use_power_db (bool): (Default: False) Whether to use the power decibel definition. If False, the amplitude decibel definition is used instead.
			
			Returns:
				'x' %s decibels.
		""" % convert_str
		return func
	return decorator

@_doc_convert_db('in')
def convert_to_db(x, use_power_db=False):
	factor = 10 if use_power_db else 20 # Power decibels or not
	return factor*_np.log10(x)          # Return converted value

@_doc_convert_db('converted from')
def convert_from_db(x, use_power_db=False):
	factor = 10 if use_power_db else 20 # Power decibels or not
	return 10 ** (x/factor)             # Return converted value

#===========
# Bandwidth
#===========

# TODO: mag -> mag_data and the like?
def _breakFreq(freq, mag, di, decibel=3, is_stop_filter=False):
	# Size check
	if freq.size != mag.size:
		raise ValueError("'freq' and 'mag' must be of the same size.")

	# Return negated if stop filter
	if is_stop_filter:
		return _breakFreq(freq, -mag, di, decibel=decibel, is_stop_filter=False)

	# Find out peak and break magnitude
	peak_index = mag.argmax()
	break_mag  = mag[peak_index]*db(-decibel, from_db = True)

	# Search
	i = peak_index
	while 0 <= i < mag.size:
		if mag[i] < break_mag:
			return freq[i]
		i += di

	# Out of bounds
	if i < 0:
		return 0.
	elif i >= mag.size:
		raise ValueError("High break frequency is not in interval.") # TODO: Only high?

# Docstring decorator for 'lo_break_freq', 'hi_break_freq' and 'bandwidth'.
def _doc_bandwidth(what_str):
	def decorator(func):
		func.__doc__ = """
			Calculates the %s of a filter.

			Args:
				freq (numpy.ndarray): Frequency data.
				mag (numpy.ndarray):  Magnitude data.

			Kwargs:
				decibel (number):      Deviation from min/max value required to qualify as break frequency, given in amplitude decibels.
				is_stop_filter (bool): Whether to treat data as a stop filter. If False, data is treated as a pass filter.

			Returns:
				float. %s
		""" % (what_str, what_str[0].upper() + what_str[1:])
		return func
	return decorator

@_doc_bandwidth('low break frequency')
def lo_break_freq(freq, mag, decibel=3, is_stop_filter=False):
	return _breakFreq(freq, mag, -1, decibel, is_stop_filter)

@_doc_bandwidth('high break frequency')
def hi_break_freq(freq, mag, decibel=3, is_stop_filter=False):
	return _breakFreq(freq, mag, 1, decibel, is_stop_filter)

@_doc_bandwidth('bandwidth')
def bandwidth(freq, mag, decibel=3, is_stop_filter=False):
	return hi_break_freq(freq, mag, decibel, is_stop_filter) - lo_break_freq(freq, mag, decibel, is_stop_filter)

#=========
# Margins
#=========

def intersects(x, y, target):
	"""
	Calculates where y = f(x) intersects target.

	Args:
		x (numpy.ndarray): x data.
		y (numpy.ndarray): y data.
		target (number):   y value for where the intersect is taken.

	Returns:
		float. x value for where y intersects target.
	"""

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
	raise ValueError("Data never intersects target.")

def unity_gain_freq(freq, mag):
	"""
	Calculates unity gain frequency from magnitude data as function of frequency.

	Args:
		freq (numpy.ndarray): Frequency data.
		mag (numpy.ndarray):  Magnitude data.

	Returns:
		float. Unity gain frequency.
	"""

	return intersects(freq, mag, 1)

def phase_180_freq(freq, phase):
	"""
	Calculates frequency of 180 degree phase shift from magnitude data as function of frequency.
	
	Args:
		freq (numpy.ndarray):  Frequency data.
		phase (numpy.ndarray): Phase data.
	
	Returns:
		float. Frequency of 180 degrees phase shift.
	"""

	freqs = []

	# Loop through all necessary phase 360-offsets
	for phase_offset in range( (int(_np.floor(min(phase))) / 360) * 360, (int(_np.ceil(max(phase))) / 360) * 360, 360): # TODO: Is int(...) necessary?
		# Error means no intersection for given phase and can therefore be ignored
		try:
			freqs.append(intersects(freq, phase - phase_offset, 180))
		except:
			pass

	if freqs:
		# First intersection is the important one
		return min(freqs)
	else:
		# There were no 180 frequency
		return Exception("Phase never intersects 180 + 360*n.")

def gain_margin(freq, mag, phase, use_power_db=False):
	"""
	Calculates gain margin from magnitude and phase data, both as functions of frequency.

	Args:
		freq (numpy.ndarray):  Frequency data.
		mag (numpy.ndarray):   Magnitude data.
		phase (numpy.ndarray): Phase data.
		use_power_db (bool):   Whether to use the power decibel definition. If False, the amplitude decibel definition is used instead.

	Returns:
		float. Gain margin in decibel.
	"""

	return -db(mag[abs(freq - phase_180_freq(freq, phase)).argmin()], use_power_db=use_power_db)

def phase_margin(freq, mag, phase):
	"""
	Calculates phase margin from magnitude and phase data, both as functions of frequency.

	Args:
		freq (numpy.ndarray):  Frequency data.
		mag (numpy.ndarray):   Magnitude data.
		phase (numpy.ndarray): Phase data.

	Returns:
		float. Phase margin.
	"""
	return 180 + phase[abs(freq - unity_gain_freq(freq, mag)).argmin()]
