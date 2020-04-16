# Copyright 2020 Joakim Nilsson
# Copyright 2005 Detlef Lannert
# Copyright 2005 Ferdinand Jamitzky
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

#=========
# Imports
#=========

from .circuit import parallel_impedance as _parallel_impedance

#================
# Implementation
#================

class _InfixPar(object):
	"""
	Infix parallel impedance operator helper class.

	Example usage:
	>>> 1 |par| 3
	0.75
	"""
	def __init__(self, function):
		self.function = function
	def __ror__(self, other):
		return _InfixPar(lambda x: self.function(other, x))
	def __or__(self, other):
		return self.function(other)

par = _InfixPar(_parallel_impedance)
