# Copyright 2017-2020 Joakim Nilsson
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

# External
import numpy as _np

# Internal
from .circuit import capacitor_impedance, inductor_impedance

#============
# Shorthands
#============

_inv = _np.linalg.inv
_det = _np.linalg.det

#====================
# Matrix conversions
#====================

# TODO: Using Z as intermediate may cause conversions to infinities/NaNs. Implement direct conversions between all parameters.
def convert_parameter_matrix(matrix, from_, to, char_imp=50):
	"""
	Converts between types of matrices representing n-port parameters.

	Valid types of parameter are the following:
	'z': impedance parameters
	'y': admittance parameters
	'h': hybrid parameters
	'g': inverse hybrid parameters
	'a': chain parameters, type a
	'b': chain parameters, type b
	's': scattering parameters
	't': scattering transfer parameters

	Args:
		matrix ([[number]]):          Matrix to convert.
		from_ (chr):                  n-port parameter type to convert from.
		to (chr):                     n-port parameter type to convert to.
		char_imp (number | [number]): (Default: 50) Characteristic impedance in case of conversion between power and amplitude parameters. If ports have different characteristic impedances, 'char_imp' can be given as a vector where element n represent the characteristic impedance for port n. [Ω]

	Returns:
		([[number]]) Converted matrix.
	"""

	# Identity matrix
	i = _np.identity(len(matrix), dtype=complex)

	# Characteristic impedance matrix
	z0 = _np.asarray(char_imp, dtype=complex)
	if z0.shape == ():
		z0 = _np.asarray([z0]*matrix.shape[0], dtype=complex)
	z0 = _np.diag(z0)

	# Root characteristic conductance matrix
	g0 = i / _np.diag(_np.sqrt(_np.real(z0)))

	# Check so that 'from_' and 'to' are valid matrix types
	for matrix_type in from_, to:
		if not matrix_type in ('z', 'y', 'g', 'h', 'a', 'b', 's', 't'):
			raise ValueError("'%s' is not a valid matrix type." % matrix_type)

	# Do not convert if input matrix type is the same as output matrix type
	if from_ == to:
		return matrix.copy()

	# Verify that matrix is square
	if matrix.shape[0] != matrix.shape[1]:
		raise ValueError('Matrix must be square.')

	# Check shape of z0
	if z0.shape[0] != matrix.shape[0]:
		raise ValueError("If non-scalar, 'char_imp' must have the same size as 'matrix'.")

	# Shape checking for a-, b- and t-parameters
	for params in ('a', 'b', 't'):
		if params in (from_, to):
			if matrix.shape != (2, 2):
				raise ValueError('%s-parameters have exactly 2 ports and must thus be a 2x2 matrix.' % params)

	#===================
	# From z-parameters
	#===================
	z = matrix

	# To y-parameters
	if (from_, to) == ('z', 'y'):
		return _inv(z)

	# To h-parameters
	if (from_, to) == ('z', 'h'):
		h = _np.ndarray((2, 2), dtype=complex)
		h[0][0] = _det(z)
		h[0][1] = z[0][1]
		h[1][0] = -z[1][0]
		h[1][1] = 1
		h /= z[1][1]
		return h

	# To g-parameters
	if (from_, to) == ('z', 'g'):
		g = _np.ndarray((2, 2), dtype=complex)
		g[0][0] = 1
		g[0][1] = -z[0][1]
		g[1][0] = z[1][0]
		g[1][1] = _det(z)
		g /= z[0][0]
		return g

	# To a-parameters
	if (from_, to) == ('z', 'a'):
		a = _np.ndarray((2, 2), dtype=complex)
		a[0][0] = z[0][0]
		a[0][1] = _det(z)
		a[1][0] = 1
		a[1][1] = z[1][1]
		a /= z[1][0]
		return a

	# To b-parameters
	if (from_, to) == ('z', 'b'):
		b = _np.ndarray((2, 2), dtype=complex)
		b[0][0] = z[1][1]
		b[0][1] = -_det(z)
		b[1][0] = -1
		b[1][1] = z[0][0]
		b /= z[0][1]
		return b

	# To s-parameters
	if (from_, to) == ('z', 's'):
		s = g0 @ (z - z0) @ _inv(z + z0) @ _inv(g0)
		return s

	# TODO: To t-parameters

	#===================
	# From y-parameters
	#===================
	y = matrix

	# To z-parameters
	if (from_, to) == ('y', 'z'):
		return _inv(y)

	# To h-parameters
	if (from_, to) == ('y', 'h'):
		h = _np.ndarray((2, 2), dtype=complex)
		h[0][0] = 1
		h[0][1] = -y[0][1]
		h[1][0] = y[1][0]
		h[1][1] = _det(y)
		h /= y[0][0]
		return h

	# To g-parameters
	if (from_, to) == ('y', 'g'):
		g = _np.ndarray((2, 2), dtype=complex)
		g[0][0] = _det(y)
		g[0][1] = y[0][1]
		g[1][0] = -y[1][0]
		g[1][1] = 1
		g /= y[1][1]
		return g

	# To a-parameters
	if (from_, to) == ('y', 'a'):
		a = _np.ndarray((2, 2), dtype=complex)
		a[0][0] = -y[1][1]
		a[0][1] = -1
		a[1][0] = -_det(y)
		a[1][1] = -y[0][0]
		a /= y[1][0]
		return a

	# To b-parameters
	if (from_, to) == ('y', 'b'):
		b = _np.ndarray((2, 2), dtype=complex)
		b[0][0] = -y[0][0]
		b[0][1] = 1
		b[1][0] = _det(y)
		b[1][1] = -y[1][1]
		b /= y[0][1]
		return b

	# To s-parameters
	if (from_, to) == ('y', 's'):
		s = g0 @ (i - (z0 @ y)) @ _inv( i + (z0 @ y)) @ _inv(g0)
		return s

	# TODO: To t-parameters

	#===================
	# From h-parameters
	#===================
	h = matrix

	# To z-parameters
	if (from_, to) == ('h', 'z'):
		z = _np.ndarray((2, 2), dtype=complex)
		z[0][0] = _det(h)
		z[0][1] = h[0][1]
		z[1][0] = -h[1][0]
		z[1][1] = 1
		z /= h[1][1]
		return z

	# To y-parameters
	if (from_, to) == ('h', 'y'):
		y = _np.ndarray((2, 2), dtype=complex)
		y[0][0] = 1
		y[0][1] = -h[0][1]
		y[1][0] = h[1][0]
		y[1][1] = _det(h)
		y /= h[0][0]
		return y

	# To g-parameters
	if (from_, to) == ('h', 'g'):
		return _inv(h)

	# To a-parameters
	if (from_, to) == ('h', 'a'):
		a = _np.ndarray((2, 2), dtype=complex)
		a[0][0] = -np.linalg.det(h)
		a[0][1] = -h[0][0]
		a[1][0] = -h[1][1]
		a[1][1] = -1
		a /= h[1][0]
		return a

	# To b-parameters
	if (from_, to) == ('h', 'b'):
		b = _np.ndarray((2, 2), dtype=complex)
		b[0][0] = 1
		b[0][1] = -h[0][0]
		b[1][0] = -h[1][1]
		b[1][1] = _det(h)
		b /= h[0][1]
		return b

	# To s-parameters
	if (from_, to) == ('h', 's'):
		s = _np.ndarray((2, 2), dtype=complex)
		s[0][0] = (h[0][0] - z0[0][0]) * (1 + z0[1][1]*h[1][1]) - z0[1][1]*h[0][1]*h[1][0]
		s[0][1] = 2 * h[0][1] * _np.sqrt(z0[0][0] * z0[1][1])
		s[1][0] = -2 * h[1][0] * _np.sqrt(z0[0][0] * z0[1][1])
		s[1][1] = (h[0][0] + z0[0][0]) * (1 - z0[1][1]*h[1][1]) + z0[1][1]*h[0][1]*h[1][0]
		s /= (h[0][0] + z0[0][0]) * (1 + z0[1][1]*h[1][1]) - z0[1][1]*h[0][1]*h[1][0]
		return s

	# TODO: To t-parameters

	#===================
	# From g-parameters
	#===================
	g = matrix

	# To z-parameters
	if (from_, to) == ('g', 'z'):
		z = _np.ndarray((2, 2), dtype=complex)
		z[0][0] = 1
		z[0][1] = -g[0][1]
		z[1][0] = g[1][0]
		z[1][1] = _det(g)
		z /= g[0][0]
		return z

	# To y-parameters
	if (from_, to) == ('g', 'y'):
		y = _np.ndarray((2, 2), dtype=complex)
		y[0][0] = _det(g)
		y[0][1] = g[0][1]
		y[1][0] = -g[1][0]
		y[1][1] = 1
		y /= g[1][1]
		return y

	# To h-parameters
	if (from_, to) == ('g', 'h'):
		return _inv(g)

	# To a-parameters
	if (from_, to) == ('g', 'a'):
		a = _np.ndarray((2, 2), dtype=complex)
		a[0][0] = 1
		a[0][1] = g[1][1]
		a[1][0] = g[0][0]
		a[1][1] = _det(g)
		a /= g[1][0]
		return a

	# To b-parameters
	if (from_, to) == ('g', 'b'):
		b = _np.ndarray((2, 2), dtype=complex)
		b[0][0] = -_det(g)
		b[0][1] = g[1][1]
		b[1][0] = g[0][0]
		b[1][1] = -1
		b /= g[0][1]
		return b

	# To s-parameters
	if (from_, to) == ('g', 's'):
		s = _np.ndarray((2, 2), dtype=complex)
		s[0][0] = (1 - g[0][0] + z0[0][0]) * (g[1][1] + z0[1][1]) + z0[1][1]*g[0][1]*g[1][0]
		s[0][1] = -2 * g[0][1] * _np.sqrt(z0[0][0] * z0[1][1])
		s[1][0] = 2 * g[1][0] * _np.sqrt(z0[0][0] * z0[1][1])
		s[1][1] = (1 + g[0][0] + z0[0][0]) * (g[1][1] - z0[1][1]) - z0[1][1]*g[0][1]*g[1][0]
		s /= (1 + g[0][0] + z0[0][0]) * (g[1][1] + z0[1][1]) - z0[1][1]*g[0][1]*g[1][0]
		return s

	# TODO: To t-parameters

	#===================
	# From a-parameters
	#===================
	a = matrix

	# To z-parameters
	if (from_, to) == ('a', 'z'):
		z = _np.ndarray((2, 2), dtype=complex)
		z[0][0] = a[0][0]
		z[0][1] = _det(a)
		z[1][0] = 1
		z[1][1] = a[1][1]
		z /= a[1][0]
		return z

	# To y-parameters
	if (from_, to) == ('a', 'y'):
		y = _np.ndarray((2, 2), dtype=complex)
		y[0][0] = a[1][1]
		y[0][1] = -_det(a)
		y[1][0] = -1
		y[1][1] = a[0][0]
		y /= a[0][1]
		return y

	# To h-parameters
	if (from_, to) == ('a', 'h'):
		h = _np.ndarray((2, 2), dtype=complex)
		h[0][0] = a[0][1]
		h[0][1] = _det(a)
		h[1][0] = -1
		h[1][1] = a[1][0]
		h /= a[1][1]
		return h

	# To g-parameters
	if (from_, to) == ('a', 'g'):
		g = _np.ndarray((2, 2), dtype=complex)
		g[0][0] = a[1][0]
		g[0][1] = -_det(a)
		g[1][0] = 1
		g[1][1] = a[0][1]
		g /= a[0][0]
		return g

	# To b-parameters
	if (from_, to) == ('a', 'b'):
		b = _np.ndarray((2, 2), dtype=complex)
		b[0][0] = a[1][1]
		b[0][1] = -a[0][1]
		b[1][0] = -a[1][0]
		b[1][1] = a[0][0]
		b /= _det(a)
		return b

	# To s-parameters
	if (from_, to) == ('a', 's'):
		s = _np.ndarray((2, 2), dtype=complex)
		s[0][0] = (
			a[0][0] * z0[1][1] +
			a[0][1] -
			a[1][0] * _np.conj(z0[0][0]) * z0[1][1] -
			a[1][1] * _np.conj(z0[0][0])
		)
		s[0][1] = 2 * _np.sqrt(_np.real(z0[0][0]) * _np.real(z0[1][1])) * _det(a)
		s[1][0] = 2 * _np.sqrt(_np.real(z0[0][0]) * _np.real(z0[1][1]))
		s[1][1] = (-
			a[0][0] * _np.conj(z0[1][1]) +
			a[0][1] -
			a[1][0] * z0[0][0] * z0[1][1] +
			a[1][1] * z0[0][0]
		)
		s /= (
			a[0][0] * z0[1][1] +
			a[0][1] +
			a[1][0] * z0[0][0] * z0[1][1] +
			a[1][1] * z0[0][0]
		)
		return s

	# TODO: To t-parameters

	#===================
	# From b-parameters
	#===================
	b = matrix

	# To z-parameters
	if (from_, to) == ('b', 'z'):
		z = _np.ndarray((2, 2), dtype=complex)
		z[0][0] = -b[1][1]
		z[0][1] = -1
		z[1][0] = -_det(b)
		z[1][1] = -b[0][0]
		z /= b[1][0]
		return z

	# To y-parameters
	if (from_, to) == ('b', 'y'):
		y = _np.ndarray((2, 2), dtype=complex)
		y[0][0] = -b[1][1]
		y[0][1] = 1
		y[1][0] = _det(b)
		y[1][1] = -b[1][1]
		y /= b[0][1]
		return y

	# To h-parameters
	if (from_, to) == ('b', 'h'):
		h = _np.ndarray((2, 2), dtype=complex)
		h[0][0] = -b[0][1]
		h[0][1] = 1
		h[1][0] = -_det(b)
		h[1][1] = -b[1][0]
		h /= b[0][0]
		return h

	# To g-parameters
	if (from_, to) == ('b', 'g'):
		g = _np.ndarray((2, 2), dtype=complex)
		g[0][0] = -b[1][0]
		g[0][1] = -1
		g[1][0] = _det(b)
		g[1][1] = -b[0][1]
		g /= b[1][1]
		return g

	# To a-parameters
	if (from_, to) == ('b', 'a'):
		a = _np.ndarray((2, 2), dtype=complex)
		a[0][0] = b[1][1]
		a[0][1] = -b[0][1]
		a[1][0] = -b[1][0]
		a[1][1] = b[0][0]
		a /= _det(b)
		return a

	# TODO: Simplify
	# To s-parameters
	if (from_, to) == ('b', 's'):
		b /= b[0][0]*b[1][1] - b[0][1]*b[1][0]
		s = _np.ndarray((2, 2), dtype=complex)
		s[0][0] = (
			b[1][1] * z0[1][1] +
			-b[0][1] -
			-b[1][0] * _np.conj(z0[0][0]) * z0[1][1] -
			b[0][0] * _np.conj(z0[0][0])
		)
		s[0][1] = 2 * _np.sqrt(_np.real(z0[0][0]) * _np.real(z0[1][1])) * _det(a)
		s[1][0] = 2 * _np.sqrt(_np.real(z0[0][0]) * _np.real(z0[1][1]))
		s[1][1] = (-
			b[1][1] * _np.conj(z0[1][1]) +
			-b[0][1] -
			-b[1][0] * z0[0][0] * z0[1][1] +
			b[0][0] * z0[0][0]
		)
		s /= (
			b[1][1] * z0[1][1] +
			-b[0][1] +
			-b[1][0] * z0[0][0] * z0[1][1] +
			b[0][0] * z0[0][0]
		)
		return s

	# TODO: To t-parameters

	#===================
	# From s-parameters
	#===================
	s = matrix
	
	# To z-parameters
	if (from_, to) == ('s', 'z'):
		z = _inv(g0) @ _inv(i - s) @ (i + s) @ z0 @ g0
		return z

	# To y-parameters
	if (from_, to) == ('s', 'y'):
		y = _inv(g0) @ _inv(z0) @ _inv(i + s) @ (i - s) @ g0
		return y

	# To h-parameters
	if (from_, to) == ('s', 'h'):
		h = _np.ndarray((2, 2), dtype=complex)
		h[0][0] = ((1 + s[0][0]) * (1 + s[1][1]) - s[0][1] * s[1][0]) * z0[0][0]
		h[0][1] = 2 * s[0][1] * _np.sqrt(z0[0][0] / z0[1][1])
		h[1][0] = -2 * s[1][0] * _np.sqrt(z0[0][0] / z0[1][1])
		h[1][1] = ((1 - s[0][0]) * (1 - s[1][1]) - s[0][1] * s[1][0]) / z0[1][1]
		h /= (1 - s[0][0]) * (1 + s[1][1]) + s[0][1] * s[1][0]
		return h

	# To g-parameters
	if (from_, to) == ('s', 'g'):
		g = _np.ndarray((2, 2), dtype=complex)
		g[0][0] = ((1 - s[0][0]) * (1 - s[1][1]) - s[0][1] * s[1][0]) / z0[0][0]
		g[0][1] = -2 * s[0][1] * _np.sqrt(z0[1][1] / z0[0][0])
		g[1][0] = 2 * s[1][0] * _np.sqrt(z0[1][1] / z0[0][0])
		g[1][1] = ((1 + s[0][0]) * (1 + s[1][1]) - s[0][1] * s[1][0]) * z0[1][1]
		g /= (1 + s[0][0]) * (1 - s[1][1]) + s[0][1] * s[1][0]
		return g

	# To a-parameters
	if (from_, to) == ('s', 'a'):
		a = _np.ndarray((2, 2), dtype=complex)
		a[0][0] = (
			_np.conj(z0[0][0]) * (1 - s[1][1]) +
			z0[0][0] * (s[0][0] - _det(s))
		)
		a[0][1] = (
			_np.conj(z0[0][0]) * _np.conj(z0[1][1]) +
			z0[0][0] * _np.conj(z0[1][1]) * s[0][0] +
			_np.conj(z0[0][0]) * z0[1][1] * s[1][1] +
			z0[0][0] * z0[1][1] * _det(s)
		)
		a[1][0] = 1 - s[0][0] - s[1][1] + _det(s)
		a[1][1] = (
			_np.conj(z0[1][1]) * (1 - s[0][0]) +
			z0[1][1] * (s[1][1] - _det(s))
		)
		a /= 2 * s[1][0] * _np.sqrt(_np.real(z0[0][0]) * _np.real(z0[1][1]))
		return a

	# To b-parameters
	if (from_, to) == ('s', 'b'):
		b = _np.ndarray((2, 2), dtype=complex)
		b[0][0] = (
			_np.conj(z0[1][1]) * (1 - s[0][0]) +
			z0[1][1] * (s[1][1] - _det(s))
		)
		b[0][1] = (-
			_np.conj(z0[0][0]) * _np.conj(z0[1][1]) -
			z0[0][0] * _np.conj(z0[1][1]) * s[0][0] -
			_np.conj(z0[0][0]) * z0[1][1] * s[1][1] -
			z0[0][0] * z0[1][1] * _det(s)
		)
		b[1][0] = -1 + s[0][0] + s[1][1] - _det(s)
		b[1][1] = (
			_np.conj(z0[0][0]) * (1 - s[1][1]) +
			z0[0][0] * (s[0][0] - _det(s))
		)
		b /= 2 * s[0][1] * _np.sqrt(_np.real(z0[0][0]) * _np.real(z0[1][1]))
		return b

	# To t-parameters
	if (from_, to) == ('s', 't'):
		t = _np.ndarray((2, 2), dtype=complex)
		t[0][0] = -_det(s)
		t[0][1] = s[0][0]
		t[1][0] = -s[1][1]
		t[1][1] = 1
		t /= s[1][0]
		return t

	#===================
	# From t-parameters
	#===================
	t = matrix

	# TODO: To z-parameters
	# TODO: To y-parameters
	# TODO: To h-parameters
	# TODO: To g-parameters
	# TODO: To a-parameters
	# TODO: To b-parameters

	# To s-parameters
	if (from_, to) == ('t', 's'):
		s = _np.ndarray((2, 2), dtype=complex)
		s[0][0] = t[0][1]
		s[0][1] = _det(t)
		s[1][0] = 1
		s[1][1] = -t[1][0]
		s /= matrix[1][1]
		return s

	#======================================================
	# Error if this conversion hasn't been implemented yet
	#======================================================
	raise NotImplementedError()

class NPortNetwork:
	"""
	Data structure for automatic conversions between n-port parameter types.

	Different representations of n-port parameters are provided by the attributes, 'z', 'y', 'g', 'h', 'a', 'b', 's', and 't'. Assigning to or modifying a parameter and then accessing another automatically converts from the former to the latter when the latter is accessed.
	
	To avoid ambiguities on which parameter type to use in an automatic conversion, only one n-port parameter representation is allowed to be modified between assignments.

	Args:
		char_imp (number | [number]): (Default: 50) Characteristic impedance in case of conversion between power and amplitude parameters. If ports have different characteristic impedances, 'char_imp' can be given as a vector where element n represent the characteristic impedance for port n. [Ω]
	"""

	def __init__(self, char_imp=50):
		self.char_imp = char_imp

		self._reset_matrices()
		self._last_assigned_matrix = None
		self._last_assigned_type   = None

	def _reset_matrices(self):
		self._z = None
		self._y = None
		self._h = None
		self._g = None
		self._a = None
		self._b = None
		self._s = None
		self._t = None

	def _check_init(self):
		if self._last_assigned_type is None:
			raise AttributeError('n-port matrix has not been initialized.')

	def _get_last_modified_matrix(self):
		num_modifications    = 0
		modified_matrix_type = None

		# Iterate through all matrix types
		for matrix_type in ('z', 'y', 'h', 'g', 'a', 'b', 's', 't'):
			# Get old matrix
			matrix = getattr(self, '_'+ matrix_type)

			# Skip uninitialized matrices
			if matrix is None:
				continue

			# Check and count modifications in matrices
			if not _np.array_equal(
					matrix,
					convert_parameter_matrix(
						self._last_assigned_matrix,
						self._last_assigned_type,
						matrix_type,
						char_imp = self.char_imp,
					)
				):
				modified_matrix_type = matrix_type
				num_modifications += 1

		# Too many modifications
		if num_modifications > 1:
			raise RuntimeError('Modifications to multiple matrix types have been performed since last matrix assignment. Modifications are allowed to at most one matrix type between matrix assignments.')

		# Update modified matrix
		elif num_modifications == 1:
			self._last_assigned_matrix = getattr(self, '_'+ modified_matrix_type)
			self._last_assigned_type   = modified_matrix_type
			self._reset_matrices()
			setattr(self, '_'+ modified_matrix_type, self._last_assigned_matrix) # Restore unnecessarily reset matrix

		# Return last assigned matrix
		return self._last_assigned_matrix

	@property
	def z(self):
		"""
		matrix ([[number]]): z-parameter matrix (impedance parameters)
		"""
		self._check_init()
		self._z = convert_parameter_matrix(
			self._get_last_modified_matrix(),
			self._last_assigned_type,
			'z',
			char_imp = self.char_imp,
		)
		return self._z

	@property
	def y(self):
		"""
		matrix ([[number]]): y-parameter matrix (admittance parameters)
		"""
		self._check_init()
		self._y = convert_parameter_matrix(
			self._get_last_modified_matrix(),
			self._last_assigned_type,
			'y',
			char_imp = self.char_imp,
		)
		return self._y

	@property
	def h(self):
		"""
		matrix ([[number]]): h-parameter matrix (hybrid parameters)
		"""
		self._check_init()
		self._h = convert_parameter_matrix(
			self._get_last_modified_matrix(),
			self._last_assigned_type,
			'h',
			char_imp = self.char_imp,
		)
		return self._h

	@property
	def g(self):
		"""
		matrix ([[number]]): g-parameter matrix (inverse hybrid parameters)
		"""
		self._check_init()
		self._g = convert_parameter_matrix(
			self._get_last_modified_matrix(),
			self._last_assigned_type,
			'g',
			char_imp = self.char_imp,
		)
		return self._g

	@property
	def a(self):
		"""
		matrix ([[number]]): a-parameter matrix (chain parameters, type a)
		"""
		self._check_init()
		self._a = convert_parameter_matrix(
			self._get_last_modified_matrix(),
			self._last_assigned_type,
			'a',
			char_imp = self.char_imp,
		)
		return self._a

	@property
	def b(self):
		"""
		matrix ([[number]]): b-parameter matrix (chain parameters, type b)
		"""
		self._check_init()
		self._b = convert_parameter_matrix(
			self._get_last_modified_matrix(),
			self._last_assigned_type,
			'b',
			char_imp = self.char_imp,
		)
		return self._b

	@property
	def s(self):
		"""
		matrix ([[number]]): s-parameter matrix (scattering parameters)
		"""
		self._check_init()
		self._s = convert_parameter_matrix(
			self._get_last_modified_matrix(),
			self._last_assigned_type,
			's',
			char_imp = self.char_imp,
		)
		return self._s

	@property
	def t(self):
		"""
		matrix ([[number]]): t-parameter matrix (scattering transfer parameters)
		"""
		self._check_init()
		self._t = convert_parameter_matrix(
			self._get_last_modified_matrix(),
			self._last_assigned_type,
			't',
			char_imp = self.char_imp,
		)
		return self._t

	@z.setter
	def z(self, matrix):
		self._reset_matrices()
		self._last_assigned_matrix = matrix.copy()
		self._last_assigned_type   = 'z'

	@y.setter
	def y(self, matrix):
		"""
		matrix ([[number]]): z-parameter matrix (impedance parameters)
		"""
		self._reset_matrices()
		self._last_assigned_matrix = matrix.copy()
		self._last_assigned_type   = 'y'

	@h.setter
	def h(self, matrix):
		"""
		matrix ([[number]]): z-parameter matrix (impedance parameters)
		"""
		self._reset_matrices()
		self._last_assigned_matrix = matrix.copy()
		self._last_assigned_type   = 'h'

	@g.setter
	def g(self, matrix):
		"""
		matrix ([[number]]): z-parameter matrix (impedance parameters)
		"""
		self._reset_matrices()
		self._last_assigned_matrix = matrix.copy()
		self._last_assigned_type   = 'g'

	@a.setter
	def a(self, matrix):
		"""
		matrix ([[number]]): z-parameter matrix (impedance parameters)
		"""
		self._reset_matrices()
		self._last_assigned_matrix = matrix.copy()
		self._last_assigned_type   = 'a'

	@b.setter
	def b(self, matrix):
		"""
		matrix ([[number]]): z-parameter matrix (impedance parameters)
		"""
		self._reset_matrices()
		self._last_assigned_matrix = matrix.copy()
		self._last_assigned_type   = 'b'

	@s.setter
	def s(self, matrix):
		"""
		matrix ([[number]]): z-parameter matrix (impedance parameters)
		"""
		self._reset_matrices()
		self._last_assigned_matrix = matrix.copy()
		self._last_assigned_type   = 's'

	@t.setter
	def t(self, matrix):
		"""
		matrix ([[number]]): z-parameter matrix (impedance parameters)
		"""
		self._reset_matrices()
		self._last_assigned_matrix = matrix.copy()
		self._last_assigned_type   = 't'

#=======================================================
# Functions for generation of various types of matrices
#=======================================================

def transmission_line_matrix(matrix_type, char_imp, prop_const, length):
	"""
		Yields a transmission line matrix.

		Args:
			matrix_type (chr):   2-port parameter type.
			char_imp (number):   Characteristic impedance of the transmission line.
			prop_const (number): Propagation constant of the transmission line.
			length (number):     Length of the transmission line.

		Returns:
			(numpy.ndarray): Transmission line cascade matrix.
	"""

	# Create a-matrix
	matrix       = _np.ndarray((2, 2), dtype=complex)
	angle        = prop_const * length
	matrix[0][0] = _np.cosh(angle)
	matrix[0][1] = _np.sinh(angle) * char_imp
	matrix[1][0] = _np.sinh(angle) / char_imp
	matrix[1][1] = _np.cosh(angle)

	# Convert to <matrix type> and return
	return convert_parameter_matrix(matrix, 'a', matrix_type, char_imp)

def transformer_matrix(matrix_type, ratio, char_imp=50):
	"""
		Yields a transformer matrix.
		Note: Transformer also works for DC.

		Args:
			matrix_type (chr): 2-port parameter type.
			ratio (number):    Transformer ratio, N. (from port 1 to port 2, N:1)
			char_imp (number): Characteristic impedance in case of conversion between power and amplitude parameters.

		Returns:
			(numpy.ndarray): Transformer cascade matrix.
	"""

	# Create a-matrix
	matrix       = _np.ndarray((2, 2), dtype=complex)
	matrix[0][0] = ratio
	matrix[0][1] = 0
	matrix[1][0] = 0
	matrix[1][1] = 1/ratio

	# Convert to <matrix type> and return
	return convert_parameter_matrix(matrix, 'a', matrix_type, char_imp)

# Docstring decorator for cascade matrix generation
def _doc_matrix_generator(topology, quantity, use_freq=False):
	def decorator(func):
		func.__doc__ = """
			Yields a %s %s matrix.

			Args:
				matrix_type (chr): 2-port parameter type.
				%s (number):      %s.%s
				char_imp (number): Characteristic impedance in case of conversion between power and amplitude parameters.

			Returns:
				(numpy.ndarray): %s %s cascade matrix.
		""" % (
			topology,
			quantity,
			quantity[:3],
			quantity[0].upper() + quantity[1:],
			'\n\t\t\t\tfreq (number):     Frequency' if use_freq else '',
			topology[0].upper() + topology[1:],
			quantity,
		)
		return func
	return decorator

@ _doc_matrix_generator('series', 'impedance')
def series_impedance_matrix(matrix_type, imp, char_imp=50):
	# Create a-matrix
	matrix       = _np.ndarray((2, 2), dtype=complex)
	matrix[0][0] = 1
	matrix[0][1] = imp
	matrix[1][0] = 0
	matrix[1][1] = 1

	# Convert to <matrix type> and return
	return convert_parameter_matrix(matrix, 'a', matrix_type, char_imp)

@ _doc_matrix_generator('shunt', 'admittance')
def shunt_admittance_matrix(matrix_type, adm, char_imp=50):
	# Create a-matrix
	matrix = _np.ndarray((2, 2), dtype=complex)
	matrix[0][0] = 1
	matrix[0][1] = 0
	matrix[1][0] = adm
	matrix[1][1] = 1

	# Convert to <matrix type> and return
	return convert_parameter_matrix(matrix, 'a', matrix_type, char_imp)

@ _doc_matrix_generator('series', 'admittance')
def series_admittance_matrix(matrix_type, adm, char_imp=50):
	return series_impedance_matrix(matrix_type, 1 / adm, char_imp=char_imp)

@ _doc_matrix_generator('shunt', 'impedance')
def shunt_impedance_matrix(matrix_type, imp, char_imp=50):
	return shunt_admittance_matrix(matrix_type, 1 / imp)

@ _doc_matrix_generator('series', 'capacitance', use_freq=True)
def series_capacitance_matrix(matrix_type, cap, freq, char_imp=50):
	return series_impedance_matrix(matrix_type, capacitor_impedance(cap, freq), char_imp=char_imp)

@ _doc_matrix_generator('shunt', 'capacitance', use_freq=True)
def shunt_capacitance_matrix(matrix_type, cap, freq, char_imp=50):
	return shunt_impedance_matrix(matrix_type, capacitor_impedance(cap, freq), char_imp=char_imp)

@ _doc_matrix_generator('series', 'inductance', use_freq=True)
def series_inductance_matrix(matrix_type, ind, freq, char_imp=50):
	return series_impedance_matrix(matrix_type, inductor_impedance(ind, freq), char_imp=char_imp)

@ _doc_matrix_generator('shunt', 'inductance', use_freq=True)
def shunt_inductance_matrix(matrix_type, ind, freq, char_imp=50):
	return shunt_impedance_matrix(matrix_type, inductor_impedance(ind, freq), char_imp=char_imp)

@ _doc_matrix_generator('series', 'resistance')
def series_resistance_matrix(matrix_type, res, char_imp=50):
	return series_impedance_matrix(matrix_type, res, char_imp=char_imp)

@ _doc_matrix_generator('shunt', 'resistance')
def shunt_resistance_matrix(matrix_type, res, char_imp=50):
	return shunt_impedance_matrix(matrix_type, res, char_imp=char_imp)

@ _doc_matrix_generator('series', 'conductance')
def series_conductance_matrix(matrix_type, con, char_imp=50):
	return series_admittance_matrix(matrix_type, con, char_imp=char_imp)

@ _doc_matrix_generator('shunt', 'conductance')
def shunt_conductance_matrix(matrix_type, con, char_imp=50):
	return shunt_admittance_matrix(matrix_type, con, char_imp=char_imp)
