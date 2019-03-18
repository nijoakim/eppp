# Copyright 2017-2019 Joakim Nilsson
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

#=========
# Imports
#=========

# External
import numpy as _np

# Internal
from .lumped_network import capacitor_impedance, inductor_impedance

#====================
# Matrix conversions
#====================

# TODO: Using Z as intermediate may cause conversions to to infinities unnecessarily. Implement direct conversions between all parameters.
def convert_parameter_matrix(matrix, from_, to, char_imp=50):
	"""
	Converts between 2-port parameters.

	Args:
		matrix ([[number]]): Matrix to convert.
		from_ (chr):         2-port parameter type to convert from.
		to (chr):            2-port parameter type to convert to.
		char_imp (number):   Characteristic impedance in case of conversion between power and amplitude parameters. (Default: 50)

	Returns:
		([[number]]) Converted matrix.
	"""

	# Check so that 'from_' and 'to' are valid matrix types
	for matrix_type in from_, to:
		if not matrix_type in ('z', 'y', 'g', 'h', 'a', 'b', 's', 't'):
			raise ValueError("'%s' is not a valid matrix type." % matrix_type)

	# Do not convert if input matrix type is the same as output matrix type
	if from_ == to:
		return matrix.copy()

	# Shape checking for a-, b- and t-parameters
	for params in ('a', 'b', 't'):
		if params in (from_, to):
			if matrix.shape != (2, 2):
				raise ValueError('%s-parameters have exactly 2 ports and thus must be a 2x2 matrix.' % params)

	#===================
	# From z-parameters
	#===================
	z = matrix

	# To y-parameters
	if (from_, to) == ('z', 'y'):
		return _np.linalg.inv(z)

	# To h-parameters
	if (from_, to) == ('z', 'h'):
		h = _np.ndarray((2, 2), dtype=z.dtype)
		h[0][0] = _np.linalg.det(z)
		h[0][1] = z[0][1]
		h[1][0] = -z[1][0]
		h[1][1] = 1
		h /= z[1][1]
		return h

	# To g-parameters
	if (from_, to) == ('z', 'g'):
		g = _np.ndarray((2, 2), dtype=z.dtype)
		g[0][0] = 1
		g[0][1] = -z[0][1]
		g[1][0] = z[1][0]
		g[1][1] = _np.linalg.det(z)
		g /= z[0][0]
		return g

	# To a-parameters
	if (from_, to) == ('z', 'a'):
		a = _np.ndarray((2, 2), dtype=z.dtype)
		a[0][0] = z[0][0]
		a[0][1] = _np.linalg.det(z)
		a[1][0] = 1
		a[1][1] = z[1][1]
		a /= z[1][0]
		return a

	# To b-parameters
	if (from_, to) == ('z', 'b'):
		b = _np.ndarray((2, 2), dtype=z.dtype)
		b[0][0] = z[1][1]
		b[0][1] = -_np.linalg.det(z)
		b[1][0] = -1
		b[1][1] = z[0][0]
		b /= z[0][1]
		return b

	# To s-parameters
	if (from_, to) == ('z', 's'):
		i = _np.identity(len(z), dtype=z.dtype)
		s = (z - (char_imp * i)) @ _np.linalg.inv(z + (char_imp * i))
		return s

	# TODO: To t-parameters

	#===================
	# From y-parameters
	#===================
	y = matrix

	# To z-parameters
	if (from_, to) == ('y', 'z'):
		return _np.linalg.inv(y)

	# To h-parameters
	if (from_, to) == ('y', 'h'):
		h = _np.ndarray((2, 2), dtype=y.dtype)
		h[0][0] = 1
		h[0][1] = -y[0][1]
		h[1][0] = y[1][0]
		h[1][1] = np.linalg.det(y)
		h /= y[0][0]
		return h

	# To g-parameters
	if (from_, to) == ('y', 'g'):
		g = _np.ndarray((2, 2), dtype=y.dtype)
		g[0][0] = np.linalg.det(y)
		g[0][1] = y[0][1]
		g[1][0] = -y[1][0]
		g[1][1] = 1
		g /= y[1][1]
		return g

	# To a-parameters
	if (from_, to) == ('y', 'a'):
		a = _np.ndarray((2, 2), dtype=y.dtype)
		a[0][0] = -y[1][1]
		a[0][1] = -1
		a[1][0] = -np.linalg.det(y)
		a[1][1] = -y[0][0]
		a /= y[1][0]
		return a

	# To b-parameters
	if (from_, to) == ('y', 'b'):
		b = _np.ndarray((2, 2), dtype=y.dtype)
		b[0][0] = -y[1][1]
		b[0][1] = 1
		b[1][0] = np.linalg.det(y)
		b[1][1] = -y[0][0]
		b /= y[0][1]
		return b

	# TODO: To s-parameters
	# TODO: To t-parameters

	#===================
	# From h-parameters
	#===================
	h = matrix

	# To z-parameters
	if (from_, to) == ('h', 'z'):
		z = _np.ndarray((2, 2), dtype=h.dtype)
		z[0][0] = np.linalg.det(h)
		z[0][1] = h[0][1]
		z[1][0] = -h[1][0]
		z[1][1] = 1
		z /= h[1][1]
		return z

	# To y-parameters
	if (from_, to) == ('h', 'y'):
		y = _np.ndarray((2, 2), dtype=h.dtype)
		y[0][0] = 1
		y[0][1] = -h[0][1]
		y[1][0] = h[1][0]
		y[1][1] = np.linalg.det(h)
		y /= h[0][0]
		return y

	# To g-parameters
	if (from_, to) == ('h', 'y'):
		return _np.linalg.inv(h)

	# To a-parameters
	if (from_, to) == ('h', 'a'):
		a = _np.ndarray((2, 2), dtype=h.dtype)
		a[0][0] = -np.linalg.det(h)
		a[0][1] = -h[0][0]
		a[1][0] = -h[1][1]
		a[1][1] = -1
		a /= h[1][0]
		return a

	# To b-parameters
	if (from_, to) == ('h', 'a'):
		a = _np.ndarray((2, 2), dtype=h.dtype)
		a[0][0] = 1
		a[0][1] = -h[0][0]
		a[1][0] = -h[1][1]
		a[1][1] = np.linalg.det(h)
		a /= h[0][1]
		return a

	# TODO: To s-parameters
	# TODO: To t-parameters

	#===================
	# From g-parameters
	#===================
	g = matrix

	# To z-parameters
	if (from_, to) == ('g', 'z'):
		z = _np.ndarray((2, 2), dtype=g.dtype)
		z[0][0] = 1
		z[0][1] = -g[0][1]
		z[1][0] = g[1][0]
		z[1][1] = np.linalg.det(g)
		z /= g[0][0]
		return z

	# To y-parameters
	if (from_, to) == ('g', 'y'):
		y = _np.ndarray((2, 2), dtype=g.dtype)
		y[0][0] = np.linalg.det(g)
		y[0][1] = g[0][1]
		y[1][0] = -g[1][0]
		y[1][1] = 1
		y /= g[1][1]
		return y

	# To h-parameters
	if (from_, to) == ('g', 'h'):
		return _np.linalg.inv(g)

	# To a-parameters
	if (from_, to) == ('g', 'a'):
		y = _np.ndarray((2, 2), dtype=g.dtype)
		y[0][0] = 1
		y[0][1] = g[1][1]
		y[1][0] = g[0][0]
		y[1][1] = np.linalg.det(g)
		y /= g[1][0]
		return y

	# To b-parameters
	if (from_, to) == ('g', 'b'):
		y = _np.ndarray((2, 2), dtype=g.dtype)
		y[0][0] = -np.linalg.det(g)
		y[0][1] = g[1][1]
		y[1][0] = g[0][0]
		y[1][1] = -1
		y /= g[0][1]
		return y

	# TODO: To s-parameters
	# TODO: To t-parameters

	#===================
	# From a-parameters
	#===================
	a = matrix

	# TODO: To z-parameters
	# TODO: To y-parameters
	# TODO: To g-parameters
	# TODO: To h-parameters
	# TODO: To b-parameters
	# TODO: To s-parameters
	# TODO: To t-parameters

	#===================
	# From b-parameters
	#===================
	b = matrix

	# To z-parameters
	if (from_, to) == ('b', 'z'):
		z = _np.ndarray((2, 2), dtype=b.dtype)
		z[0][0] = -b[1][1]
		z[0][1] = -1
		z[1][0] = -_np.linalg.det(b)
		z[1][1] = -b[0][0]
		z /= b[1][0]
		return z

	# TODO: To z-parameters
	# TODO: To y-parameters
	# TODO: To g-parameters
	# TODO: To h-parameters
	# TODO: To a-parameters
	# TODO: To s-parameters
	# TODO: To t-parameters

	#===================
	# From s-parameters
	#===================
	s = matrix
	
	# To z-parameters
	if (from_, to) == ('s', 'z'):
		i = _np.identity(len(s), dtype=s.dtype)
		z     = char_imp * (i + s) @ _np.linalg.inv(i - s)
		return z

	# TODO: To y-parameters
	# TODO: To g-parameters
	# TODO: To h-parameters
	# TODO: To a-parameters
	# TODO: To b-parameters

	# TODO: Verify this extra carefully
	# To t-parameters
	if (from_, to) == ('s', 't'):
		t = _np.ndarray((2, 2), dtype=s.dtype)
		t[0][0] = 1
		t[0][1] = -s[1][1]
		t[1][0] = s[0][0]
		t[1][1] = -_np.linalg.det(s)
		t /= s[1][0]
		return t

	#===================
	# From t-parameters
	#===================
	t = matrix

	# TODO: To z-parameters
	# TODO: To y-parameters
	# TODO: To g-parameters
	# TODO: To h-parameters
	# TODO: To a-parameters
	# TODO: To b-parameters

	# To s-parameters
	if (from_, to) == ('t', 's'):
		s = _np.ndarray((2, 2), dtype=t.dtype)
		s[0][0] = t[1][0]
		s[0][1] = _np.linalg.det(t)
		s[1][0] = 1
		s[1][1] = -t[0][1]
		s /= matrix[0][0]
		return s

	#======================================================
	# Error if this conversion hasn't been implemented yet
	#======================================================
	raise NotImplementedError()

# TODO: Internal ndarray which is accessed by getters and setters?
# TODO: Make a copy each time a matrix is getted and check for modifications?
class NPortNetwork:
	"""
		TODO
	"""

	def __init__(self):
		self._z                = None
		self._y                = None
		self._h                = None
		self._g                = None
		self._a                = None
		self._b                = None
		self._last_assigned_as = None

	def _check_init(self):
		if self._last_assigned_as is None:
			raise AttributeError('n-port matrix has not been initialized.')

	def _get_last_assigned_matrix(self):
		return getattr(self, '_'+ self._last_assigned_as)

	def modify_inplace(self, matrix_type):
		setattr(self, matrix_type, getattr(self, matrix_type))

	@property
	def z(self):
		self._check_init()
		return convert_parameter_matrix(
			self._get_last_assigned_matrix(),
			self._last_assigned_as,
			'z',
		)

	@property
	def y(self):
		self._check_init()
		return convert_parameter_matrix(
			self._get_last_assigned_matrix(),
			self._last_assigned_as,
			'y',
		)

	@property
	def h(self):
		self._check_init()
		return convert_parameter_matrix(
			self._get_last_assigned_matrix(),
			self._last_assigned_as,
			'h',
		)

	@property
	def g(self):
		self._check_init()
		return convert_parameter_matrix(
			self._get_last_assigned_matrix(),
			self._last_assigned_as,
			'g',
		)

	@property
	def a(self):
		self._check_init()
		return convert_parameter_matrix(
			self._get_last_assigned_matrix(),
			self._last_assigned_as,
			'a',
		)

	@property
	def b(self):
		self._check_init()
		return convert_parameter_matrix(
			self._get_last_assigned_matrix(),
			self._last_assigned_as,
			'b',
		)

	@property
	def s(self):
		self._check_init()
		return convert_parameter_matrix(
			self._get_last_assigned_matrix(),
			self._last_assigned_as,
			's',
		)

	@property
	def t(self):
		self._check_init()
		return convert_parameter_matrix(
			self._get_last_assigned_matrix(),
			self._last_assigned_as,
			't',
		)

	@z.setter
	def z(self, matrix):
		self._z = matrix
		self._last_assigned_as = 'z'

	@y.setter
	def y(self, matrix):
		self._y = matrix
		self._last_assigned_as = 'y'

	@h.setter
	def h(self, matrix):
		self._h = matrix
		self._last_assigned_as = 'h'

	@g.setter
	def g(self, matrix):
		self._g = matrix
		self._last_assigned_as = 'g'

	@a.setter
	def a(self, matrix):
		self._a = matrix
		self._last_assigned_as = 'a'

	@b.setter
	def b(self, matrix):
		self._b = matrix
		self._last_assigned_as = 'b'

	@s.setter
	def s(self, matrix):
		self._s = matrix
		self._last_assigned_as = 's'

	@t.setter
	def t(self, matrix):
		self._t = matrix
		self._last_assigned_as = 't'

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
