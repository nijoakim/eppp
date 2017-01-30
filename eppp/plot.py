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

import matplotlib.pyplot as _pyplot
from .error import _string_or_exception

def bode(freq, mag, phase, power = False, title_text = ''):
	"""
	Plot a bode plot from magnitude and phase data, both as functions of frequency.
	
	Args:
		freq (numpy.ndArray):  Frequency data
		mag (numpy.ndArray):   Magnitude data
		phase (numpy.ndArray): Phase data
	
	Kwargs:
		power (bool):     Whether to use the power decibel definition. If False, the amplitude decibel definition is used instead.
		title_text (str): Title text
	"""
	
	# Size check
	if freq.size != mag.size != phase.size:
		return _string_or_exception("'freq' and 'mag' and 'phase' must be of the same size.")
	
	# Magnitude plot
	_pyplot.subplot(211)
	_pyplot.plot(freq, convert_db(mag, power = power))
	_pyplot.xscale('log')
	_pyplot.ylabel('Magnitude [convert_db]')
	
	# Title text
	_pyplot.title(title_text)
	
	# Phase plot
	_pyplot.subplot(212)
	_pyplot.plot(freq, phase)
	_pyplot.xscale('log')
	_pyplot.ylabel('Phase [degrees]')
	
	# x-label
	_pyplot.xlabel('Frequency [Hz]')

def heatmap(data, title_text = 'Heatmap', axes_unit = 'um', quantity_str = 'Magnitude [1]'):
	# Data
	x   = data['x']
	y   = data['y']
	mag = data['mag']
	
	# Plot heatmap
	_pyplot.hist2d(
		x, y,
		weights = mag,
		bins = (len(_pyplot.unique(x)), len(_pyplot.unique(y))),
	) 
	
	# Plot colorbar
	cb = _pyplot.colorbar()
	cb.set_label(quantity_str)
	
	# Title text
	_pyplot.title(title_text)
	
	# Axis labels
	_pyplot.xlabel('x-position [%s]' % axes_unit)
	_pyplot.ylabel('y-position [%s]' % axes_unit)
