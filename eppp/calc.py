# Copyright 2014-2025 Joakim Nilsson
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

# TODO: Document errors.
# TODO: Array length error checks.

#=========
# Imports
#=========

# External
import numpy           as _np
import scipy.constants as _sp_c
from math import inf

#=====================
# Decibel conversions
#=====================

def from_db(x, db_type):
	"""
	Converts a number from its decibel form.
	
	Args:
		x:                Decibel value to convert from. [dB]
		db_type (string): Whether to use the power decibel or amplitude decibel definition. Valid values are 'power' and 'amplitude'.
	
	Returns:
		'x' converted from decibels.
	"""

	# Error checking
	if not db_type in ('power', 'amplitude'):
		raise ValueError("'db_type' must be either 'power' or 'amplitude'.")

	# Conversion
	factor = 10 if db_type == 'power' else 20 # Power decibels or not
	return 10 ** (x/factor)                   # Return converted value

def to_db(x, db_type):
	"""
	Converts a number to its decibel form.
	
	Args:
		x:                Number to be converted.
		db_type (string): Whether to use the power decibel or amplitude decibel definition. Valid values are 'power' and 'amplitude'.
	
	Returns:
		'x' in decibels.
	"""

	# Error checking
	if not db_type in ('power', 'amplitude'):
		raise ValueError("'db_type' must be either 'power' or 'amplitude'.")

	# Conversion
	factor = 10 if db_type == 'power' else 20 # Power decibels or not
	return factor*_np.log10(x)                # Return converted value

#====================
# Physical phenomena
#====================

def speed_of_light(rel_permittivity=1, rel_permeability=1):
	"""
	Calculates the speed of light in a medium with given permittivity and permeability.

	Args:
		rel_permittivity (number): Relative permittivity of the medium.
		rel_permeability (number): Relative permeability of the medium.

	Returns:
		float. Speed of light. [m/s²]
	"""

	permittivity = rel_permittivity * _sp_c.epsilon_0
	permeability = rel_permeability * _sp_c.mu_0
	return 1/_np.sqrt(permittivity * permeability)

def wavelength(
		freq,
		rel_permittivity = None,
		rel_permeability = None,
		speed            = None,
	):
	"""
	Calculates the wavelength of an electromagnetic wave in a medium with given permittivity and permeability. Alternatively, the speed of the wave in the medium can be specified.

	Args:
		freq (number):             Frequency. [Hz]
		rel_permittivity (number): (default: 1) Relative permittivity of the medium.
		rel_permeability (number): (default: 1) Relative permeability of the medium.
		speed (number):            Speed of the wave in medium. [m/s]

	Returns:
		float. Wavelength. [m]
	"""

	# Error checking
	if not speed is None:
		if not rel_permittivity is None \
		or not rel_permeability is None:
			raise ValueError('Can not specify permittivity or permeability if speed is also specified speed.')

	# Default values for permittivity and permeability
	rel_permittivity = 1 if rel_permittivity is None else rel_permittivity
	rel_permeability = 1 if rel_permeability is None else rel_permeability

	# Calculate speed based on permittivity and permeability
	if speed is None:
		speed = speed_of_light(
			rel_permittivity = rel_permittivity,
			rel_permeability = rel_permeability,
		)

	# Return wavelength
	return speed / freq

def skin_depth(
		resistivity,
		freq,
		rel_permittivity = 1,
		rel_permeability = 1,
	):
	"""
	Calculates the skin depth in a material.

	Args:
		resistivity (number):      Resistivity of the material. [Ω/m]
		freq (number):             Frequency. [Hz]
		rel_permittivity (number): (Default: 1) Relative permittivity of the material.
		rel_permeability (number): (Default: 1) Relative permeability of the material.

	Returns:
		float. Skin depth. [m]
	"""

	ang_freq     = 2 * _sp_c.pi * freq
	permittivity = rel_permittivity * _sp_c.epsilon_0
	permeability = rel_permeability * _sp_c.mu_0
	a            = resistivity * ang_freq * permittivity

	return _np.sqrt(2 * resistivity / (ang_freq * permeability)) * _np.sqrt(_np.sqrt(1 + a**2) + a)

def wire_resistance(
		resistivity,
		radius,
		length,
		freq             = 0,
		rel_permittivity = 1,
		rel_permeability = 1,
	):
	"""
	Calculates the resistance of a wire. Takes the skin effect into account, but uses the approximation that either radius >> skin depth or skin depth >> radius.

	Args:
		resistivity (number):      Resistivity of the wire. [Ω/m]
		radius (number):           Radius of the wire. [m]
		length (number):           Length of the wire. [m]
		freq (number):             (Default: 0) Frequency. [Hz]
		rel_permittivity (number): (Default: 1) Relative permittivity of the wire.
		rel_permeability (number): (Default: 1) Relative permeability of the wire.

	Returns:
		float. Wire resistance. [Ω]
	"""
	# Zero radius yields infinite resistance
	if radius == 0:
		return inf

	# Require positive radius
	elif radius < 0:
		raise ValueError("'radius' must be positive'.")

	# DC resistance
	if freq == 0:
		area = _np.pi * radius**2
		return resistivity * length / area

	# AC resistance
	else:
		depth = skin_depth(
			resistivity      = resistivity,
			freq             = freq,
			rel_permittivity = rel_permittivity,
			rel_permeability = rel_permeability,
		)

		conductance = \
			1 / wire_resistance(resistivity, radius,               length) - \
			1 / wire_resistance(resistivity, max(radius-depth, 0), length)

		return 1 / conductance

def plates_capacitance(
		area,
		sep,
		rel_permittivity = 1,
	):
	"""
	Calculates the capacitance of two aligned parallel plates of equal area. Assumes plate dimension >> place separation and hence ignores fringe capacitance.

	Args:
		area (number):             Area of the plates. [m²]
		sep (number):              Distance between the two plates. [m]
		rel_permittivity (number): (Default: 1) Relative permittivity of the wire of the medium between the plates.

	Returns:
		float. Parallel plates capacitance. [F]
	"""
	return rel_permittivity * _sp_c.epsilon_0 * area / sep

#==============================
# Empirical physical phenomena
#==============================

# TODO: More substances and temperatures

# TODO: Add to 'utils.py'
def electron_mobility(carrier_conc, temp=300, substance="Si"):
	"""
	Calculates the electron mobility in a given substance and for a given temperature.

	Args:
		carrier_conc (number): Total electron concentration. [carriers/m³]
		temp (number):         (Default: 300) Temperature. [K]
		substance (string):    (Default: "Si") Semiconductor substance.

	Returns:
		float. Electron mobility. [m²/Vs]
	"""

	if substance == "Si":
		if temp == 300:
			return 131.8e-3 / (1 + (carrier_conc / 1.0e23) ** 0.85) + 9.2e-3
		raise NotImplementedError('No implementation for temperatures other than 300 K')
	else:
		raise NotImplementedError('Substance '+ substance +' has not been implemented.')

# TODO: Add to 'utils.py'
def hole_mobility(carrier_conc, temp=300, substance="Si"):
	"""
	Calculates the hole mobility in a given substance and for a given temperature.

	Args:
		carrier_conc (number): Total hole concentration. [carriers/m³]
		temp (number):         (Default: 300) Temperature. [K]
		substance (string):    (Default: "Si") Semiconductor substance.

	Returns:
		float. Hole mobility. [m²/Vs]
	"""

	if substance == "Si":
		if temp == 300:
			return 42.0e-3 / (1 + (carrier_conc / 1.6e23) ** 0.7) + 5.0e-3
		raise NotImplementedError('No implementation for temperatures other than 300 K')
	else:
		raise NotImplementedError('Substance '+ substance +' has not been implemented.')

#==========
# Q Factor
#==========

# TODO: Parallel resistance option? res_type='ser'?
# TODO: Use in utils
def solve_q_relation(freq=None, q=None, res=None, cap=None, ind=None):
	"""
	TODO
	"""

	# Error handling
	if (cap, ind).count(None) == 0:
		if cap * ind > 0 \
		or (cap == 0 and ind == 0):
			raise ValueError("If both 'cap' and 'ind' are specified, exactly one of them must be negative, indicating not to use that argument.")
	if (freq, q, res, cap, ind).count(None) != 2:
		raise ValueError("Must specify 3 arguments")

	# Calculate angular frequency
	if not freq is None:
		ang_freq = 2 * _np.pi * freq

	# Return frequency
	if freq is None:
		if not cap is None:
			return q * res / (2 * _np.pi / ind)
		elif not ind is None:
			return q * res * 2 *_np.pi * cap

	# Return Q factor
	if q is None:
		if not cap is None:
			print('q')
			return 1 / (ang_freq * cap * res)
		elif not ind is None:
			return ang_freq * ind / res

	# Return series resistance
	if res is None:
		if not cap is None:
			return 1 / (ang_freq * cap * q)
		elif not ind is None:
			return ang_freq * ind / q

	# Return capacitance or inductance
	if cap >= 0:
		return 1 / (ang_freq * res * q)
	elif ind >= 0:
		return ang_freq * ind / q

#===========
# Bandwidth
#===========

def _breakFreq(freqs, mags, di, decibel=3, is_stop_filter=False):
	# Size check
	if freqs.size != mags.size:
		raise ValueError("'freqs' and 'mags' must be of the same size.")

	# Return negated if stop filter
	if is_stop_filter:
		return _breakFreq(freqs, -mags, di, decibel=decibel, is_stop_filter=False)

	# Find out peak and break magnitude
	peak_index = mags.argmax()
	break_mags = mags[peak_index]*db(-decibel, from_db = True)

	# Search
	i = peak_index
	while 0 <= i < mags.size:
		if mags[i] < break_mag:
			return freqs[i]
		i += di

	# Out of bounds
	if i < 0:
		return 0.
	elif i >= mags.size:
		raise ValueError("High break frequency is not in interval.") # TODO: Only high?

# Docstring decorator for 'lo_break_freq', 'hi_break_freq' and 'bandwidth'.
def _doc_bandwidth(what_str):
	def decorator(func):
		func.__doc__ = """
			Calculates the %s of a filter.

			Args:
				freqs (numpy.ndarray): Frequency data.
				mags (numpy.ndarray):  Magnitude data.

			Kwargs:
				decibel (number):      Deviation from min/max value required to qualify as break frequency, given in amplitude decibels.
				is_stop_filter (bool): Whether to treat data as a stop filter. If False, data is treated as a pass filter.

			Returns:
				float. %s
		""" % (what_str, what_str[0].upper() + what_str[1:])
		return func
	return decorator

@_doc_bandwidth('low break frequency')
def lo_break_freq(freqs, mags, decibel=3, is_stop_filter=False):
	return _breakFreq(freqs, mags, -1, decibel, is_stop_filter)

@_doc_bandwidth('high break frequency')
def hi_break_freq(freqs, mags, decibel=3, is_stop_filter=False):
	return _breakFreq(freqs, mags, 1, decibel, is_stop_filter)

@_doc_bandwidth('bandwidth')
def bandwidth(freqs, mags, decibel=3, is_stop_filter=False):
	return hi_break_freq(freqs, mags, decibel, is_stop_filter) - lo_break_freq(freqs, mag, decibel, is_stop_filter)

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

	# Negate if below zero, return first if already intersects
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

def unity_gain_freq(freqs, mags):
	"""
	Calculates unity gain frequency from magnitude data as function of frequency.

	Args:
		freqs (numpy.ndarray): Frequency data.
		mags (numpy.ndarray):  Magnitude data.

	Returns:
		float. Unity gain frequency.
	"""

	try:
		return intersects(freqs, mags, 1)
	except ValueError:
		raise ValueError("Data never intersects zero.")

# TODO: Radian is the SI unit. Allow the use of radians or have radians as the default even?

def phase_180_freq(freqs, phases):
	"""
	Calculates frequency of 180 degree phase shift from magnitude data as function of frequency.
	
	Args:
		freqs (numpy.ndarray):  Frequency data.
		phases (numpy.ndarray): Phase data.
	
	Returns:
		float. Frequency of 180 degrees phase shift.
	"""

	_180_freqs = [] # TODO: Better name

	# Loop through all necessary phase 360-offsets
	for phase_offset in range( (int(_np.floor(min(phases))) / 360) * 360, (int(_np.ceil(max(phases))) / 360) * 360, 360): # TODO: Is int(...) necessary?
		# Error means no intersection for given phase and can therefore be ignored
		try:
			_180_freqs.append(intersects(freqs, phases - phase_offset, 180))
		except ValueError:
			pass

	if _180_freqs:
		# First intersection is the important one
		return min(_180_freqs)
	else:
		# There were no 180 frequency
		return ValueError("Phase never intersects 180 + 360*n.")

def gain_margin(freqs, mags, phases, db_type):
	"""
	Calculates gain margin from magnitude and phase data, both as functions of frequency.

	Args:
		freqs (numpy.ndarray):  Frequency data.
		mags (numpy.ndarray):   Magnitude data.
		phases (numpy.ndarray): Phase data.
		db_type (string):       Whether to use the power decibel or amplitude decibel definition. Valid values are 'power' and 'amplitude'.

	Returns:
		float. Gain margin. [dB]
	"""

	return -to_db(mags[abs(freqs - phase_180_freq(freqs, phases)).argmin()], db_type)

def phase_margin(freqs, mags, phases):
	"""
	Calculates phase margin from magnitude and phase data, both as functions of frequency.

	Args:
		freqs (numpy.ndarray):  Frequency data.
		mags (numpy.ndarray):   Magnitude data.
		phases (numpy.ndarray): Phase data.

	Returns:
		float. Phase margin. [degrees]
	"""
	return 180 + phases[abs(freqs - unity_gain_freq(freqs, mags)).argmin()]
