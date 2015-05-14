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

import pylab as _pl
from calc import *
from error import _stringOrException

def bode(freq, mag, phase, power = False, titleText = ''):
	"""
	Plot a bode plot from magnitude and phase data, both as functions of frequency.
	
	Args:
		freq (numpy.ndArray):  Frequency data
		mag (numpy.ndArray):   Magnitude data
		phase (numpy.ndArray): Phase data
	
	Kwargs:
		power (bool):    Whether to use the power decibel definition. If False, the amplitude decibel definition is used instead.
		titleText (str): Title text
	"""
	
	# Size check
	if freq.size != mag.size != phase.size:
		return _stringOrException("'freq' and 'mag' and 'phase' must be of the same size.")
	
	# Magnitude plot
	_pl.subplot(211)
	_pl.plot(freq, dB(mag, power = power))
	_pl.xscale('log')
	_pl.ylabel('Magnitude [dB]')
	
	# Title text
	_pl.title(titleText)
	
	# Phase plot
	_pl.subplot(212)
	_pl.plot(freq, phase)
	_pl.xscale('log')
	_pl.ylabel('Phase [degrees]')
	
	# x-label
	_pl.xlabel('Frequency [Hz]')

def heatmap(data, titleText = 'Heatmap', axesUnit = 'um', quantityStr = 'Magnitude [1]'):
	# Data
	x   = data['x']
	y   = data['y']
	mag = data['mag']
	
	# Plot heatmap
	_pl.hist2d(
		x, y,
		weights = mag,
		bins = (len(_pl.unique(x)), len(_pl.unique(y))),
	) 
	
	# Plot colorbar
	cb = _pl.colorbar()
	cb.set_label(quantityStr)
	
	# Title text
	_pl.title(titleText)
	
	# Axis labels
	_pl.xlabel('x-position [%s]' % axesUnit)
	_pl.ylabel('y-position [%s]' % axesUnit)
