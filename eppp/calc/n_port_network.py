# Copyright 2017-2018 Joakim Nilsson
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

def convert_parameter_matrix(matrix, from_, to, char_imp=50):
	"""
	Converts between 2-port parameters.

	Args:
		matrix ([[number]]): Matrix to convert.
		from_ (chr):         2-port parameter type to convert from.
		to (chr):            2-port parameter type to convert to.
		char_imp (number):   Characteristic impedance in case of conversion between power and amplitude parameters.

	Returns:
		([[number]]) Converted matrix.
	"""

	# Check so that 'from_' and 'to' are valid matrix types
	VALID_MATRIX_TYPES = ['z', 'y', 'g', 'h', 'a', 'b', 's', 't']
	for matrix_type in from_, to:
		if not matrix_type in VALID_MATRIX_TYPES:
			raise ValueError("'"+ matrix_type + "' is not a valid matrix type.")

	# Do not convert if input matrix type is the same as output matrix type
	if from_ == to:
		return matrix.copy()

	# Shape checking for a-, b- and t-parameters
	for params in ('a', 'b', 't'):
		if params in (from_, to):
			if matrix.shape != (2, 2):
				raise ValueError('%s-parameters have exactly 2 ports and thus must be a 2x2 matrix.' % params)

	# Convert from t- to s-parameters without intermediate conversion
	if from_ == 't':
		# Convert to s-parameters
		matrix_s       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_s[0][0] = matrix[1][0]
		matrix_s[0][1] = _np.linalg.det(matrix)
		matrix_s[1][0] = 1
		matrix_s[1][1] = -matrix[0][1]
		matrix_s /= matrix[0][0]

		# Convert to <to>-parameters and return
		return convert_parameter_matrix(matrix_s, 's', to, char_imp=char_imp)

	# Convert from s- to t-parameters without intermediate conversion
	if to == 't':
		# Convert to s-parameters
		matrix_t = convert_parameter_matrix(matrix, from_, 's', char_imp=char_imp)

		# Convert to t-parameters and return
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = 1
		matrix_out[0][1] = -matrix_t[1][1]
		matrix_out[1][0] = matrix_t[0][0]
		matrix_out[1][1] = -_np.linalg.det(matrix_t)
		matrix_out /= matrix[1][0]
		return matrix_out

	# Use z-parameters as intermediate conversion type
	if not 'z' in (from_, to):
		matrix = convert_parameter_matrix(matrix, from_, 'z', char_imp=char_imp) # Convert to z-parameters
		matrix = convert_parameter_matrix(matrix, 'z',   to,  char_imp=char_imp) # Convert to <to>-parameters
		return matrix

	# Symmetric conversions to and from z-parameters
	if   'y' in (from_, to):
		return _np.linalg.inv(matrix)
	elif 'h' in (from_, to):
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = _np.linalg.det(matrix)
		matrix_out[0][1] = matrix[0][1]
		matrix_out[1][0] = -matrix[1][0]
		matrix_out[1][1] = 1
		matrix_out /= matrix[1][1]
		return matrix_out
	elif 'g' in (from_, to):
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = 1
		matrix_out[0][1] = -matrix[0][1]
		matrix_out[1][0] = matrix[1][0]
		matrix_out[1][1] = _np.linalg.det(matrix)
		matrix_out /= matrix[0][0]
		return matrix_out
	elif 'a' in (from_, to):
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = matrix[0][0]
		matrix_out[0][1] = _np.linalg.det(matrix)
		matrix_out[1][0] = 1
		matrix_out[1][1] = matrix[1][1]
		matrix_out /= matrix[1][0]
		return matrix_out

	# Asymmetric conversions to and from z-parameters
	if   (from_, to) == ('z', 'b'):
		matrix_b       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_b[0][0] = matrix[1][1]
		matrix_b[0][1] = -_np.linalg.det(matrix)
		matrix_b[1][0] = -1
		matrix_b[1][1] = matrix[0][0]
		matrix_b /= matrix[0][1]
		return matrix_b
	elif (from_, to) == ('b', 'z'):
		matrix_z       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_z[0][0] = -matrix[1][1]
		matrix_z[0][1] = -1
		matrix_z[1][0] = -_np.linalg.det(matrix)
		matrix_z[1][1] = -matrix[0][0]
		matrix_z /= matrix[1][0]
		return matrix_z
	elif (from_, to) == ('z', 's'):
		matrix_ident = _np.identity(len(matrix), dtype=matrix.dtype)
		matrix_s     = (matrix - (char_imp * matrix_ident)) @ _np.linalg.inv(matrix + (char_imp * matrix_ident))
		return matrix_s
	elif (from_, to) == ('s', 'z'):
		matrix_ident = _np.identity(len(matrix), dtype=matrix.dtype)
		matrix_z     = char_imp * (matrix_ident + matrix) @ _np.linalg.inv(matrix_ident - matrix)
		return matrix_z

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

#===========================
# Cascade matrix generation
#===========================

# Docstring decorator for cascade matrix generation
def _doc_matrix_generator(topology, quantity, use_freq=False):
	def decorator(func):
		func.__doc__ = """
			Yields a %s %s matrix of cascade parameters type.

			Args:
				matrix_type (chr): 2-port parameter type ('a' or 'b').
				%s (number):      %s.%s

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
def series_impedance_matrix(matrix_type, imp):
	matrix = _np.ndarray((2, 2), dtype=complex)
	if matrix_type == 'a':
		matrix[0][0] = 1
		matrix[0][1] = imp
		matrix[1][0] = 0
		matrix[1][1] = 1
	elif matrix_type == 'b':
		matrix[0][0] = 1
		matrix[0][1] = -imp
		matrix[1][0] = 0
		matrix[1][1] = 1
	else:
		raise ValueError('Unsupported matrix type.')
	return matrix

@ _doc_matrix_generator('shunt', 'admittance')
def shunt_admittance_matrix(matrix_type, adm):
	matrix = _np.ndarray((2, 2), dtype=complex)
	if matrix_type == 'a':
		matrix[0][0] = 1
		matrix[0][1] = 0
		matrix[1][0] = adm
		matrix[1][1] = 1
	elif matrix_type == 'b':
		matrix[0][0] = 1
		matrix[0][1] = 0
		matrix[1][0] = -adm
		matrix[1][1] = 1
	else:
		raise ValueError('Unsupported matrix type.')
	return matrix

@ _doc_matrix_generator('series', 'admittance')
def series_admittance_matrix(matrix_type, adm):
	return series_impedance_matrix(matrix_type, 1 / adm)

@ _doc_matrix_generator('shunt', 'impedance')
def shunt_impedance_matrix(matrix_type, imp):
	return shunt_admittance_matrix(matrix_type, 1 / imp)

@ _doc_matrix_generator('series', 'capacitance', use_freq=True)
def series_capacitance_matrix(matrix_type, cap, freq):
	return series_impedance_matrix(matrix_type, capacitor_impedance(cap, freq))

@ _doc_matrix_generator('shunt', 'capacitance', use_freq=True)
def shunt_capacitance_matrix(matrix_type, cap, freq):
	return shunt_impedance_matrix(matrix_type, capacitor_impedance(cap, freq))

@ _doc_matrix_generator('series', 'inductance', use_freq=True)
def series_inductance_matrix(matrix_type, ind, freq):
	return series_impedance_matrix(matrix_type, inductor_impedance(ind, freq))

@ _doc_matrix_generator('shunt', 'inductance', use_freq=True)
def shunt_inductance_matrix(matrix_type, ind, freq):
	return shunt_impedance_matrix(matrix_type, inductor_impedance(ind, freq))

@ _doc_matrix_generator('series', 'resistance')
def series_resistance_matrix(matrix_type, res):
	return series_impedance_matrix(matrix_type, res)

@ _doc_matrix_generator('shunt', 'resistance')
def shunt_resistance_matrix(matrix_type, res):
	return shunt_impedance_matrix(matrix_type, res)

@ _doc_matrix_generator('series', 'conductance')
def series_conductance_matrix(matrix_type, con):
	return series_admittance_matrix(matrix_type, con)

@ _doc_matrix_generator('shunt', 'conductance')
def shunt_conductance_matrix(matrix_type, con):
	return shunt_admittance_matrix(matrix_type, con)
