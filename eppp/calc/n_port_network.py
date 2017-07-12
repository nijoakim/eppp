# Copyright 2017 Joakim Nilsson
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
from .lumped_network import capacitor_imp, inductor_imp

#=======
# Other
#=======

# TODO: s-parameters, t-parameters (also conversion between power/energy to voltage/current type parameters)

def convert_parameter_matrix(matrix, from_, to):
	"""
		TODO
	"""

	# Check so that 'from_' and 'to' are valid matrix types
	VALID_MATRIX_TYPES = ['z', 'y', 'g', 'h', 'a', 'b', 's', 't']
	for matrix_type in from_, to:
		if not matrix_type in VALID_MATRIX_TYPES:
			raise ValueError("'"+ matrix_type + "' is not a valid matrix type.")

	# Do not convert if input matrix type is the same as output matrix type
	if from_ == to:
		return matrix

	# Use z-parameters as intermediate conversion type
	if not 'z' in (from_, to):
		matrix = convert_parameter_matrix(matrix, from_, 'z') # Convert to z-parameters
		matrix = convert_parameter_matrix(matrix, 'z',   to)  # Convert to 'to'-parameters
		return matrix

	# Symmetric conversions
	if   'y' in (from_, to):
		return _np.linalg.inv(matrix)
	elif 'h' in (from_, to):
		if matrix.shape != (2, 2):
			raise ValueError('h-parameters have exactly 2 ports and thus must be a 2x2 matrix.')
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = _np.linalg.det(matrix)
		matrix_out[0][1] = matrix[0][1]
		matrix_out[1][0] = -matrix[1][0]
		matrix_out[1][1] = 1
		matrix_out /= matrix[1][1]
		return matrix_out
	elif 'g' in (from_, to):
		if matrix.shape != (2, 2):
			raise ValueError('g-parameters have exactly 2 ports and thus must be a 2x2 matrix.')
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = 1
		matrix_out[0][1] = -matrix[0][1]
		matrix_out[1][0] = matrix[1][0]
		matrix_out[1][1] = _np.linalg.det(matrix)
		matrix_out /= matrix[0][0]
		return matrix_out
	elif 'a' in (from_, to):
		if matrix.shape != (2, 2):
			raise ValueError('a-parameters have exactly 2 ports and thus must be a 2x2 matrix.')
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = matrix[0][0]
		matrix_out[0][1] = _np.linalg.det(matrix)
		matrix_out[1][0] = 1
		matrix_out[1][1] = matrix[1][1]
		matrix_out /= matrix[1][0]
		return matrix_out

	# Asymmetric conversions
	if   (from_, to) == ('z', 'b'):
		if matrix.shape != (2, 2):
			raise ValueError('b-parameters have exactly 2 ports and thus must be a 2x2 matrix.')
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = matrix[1][1]
		matrix_out[0][1] = -_np.linalg.det(matrix)
		matrix_out[1][0] = -1
		matrix_out[1][1] = matrix[0][0]
		matrix_out /= matrix[0][1]
		return matrix_out
	elif (from_, to) == ('b', 'z'):
		if matrix.shape != (2, 2):
			raise ValueError('b-parameters have exactly 2 ports and thus must be a 2x2 matrix.')
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = -matrix[1][1]
		matrix_out[0][1] = -1
		matrix_out[1][0] = -_np.linalg.det(matrix)
		matrix_out[1][1] = -matrix[0][0]
		matrix_out /= matrix[1][0]
		return matrix_out

	raise NotImplementedError()

class NPortNetwork:
	"""
		TODO
	"""
	
	# TODO: s- and t-parameters

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

# TODO: Doctrings for '*_impedance_matrix'

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

def series_admittance_matrix(matrix_type, adm):
	return series_impedance_matrix(matrix_type, 1 / adm)
def shunt_impedance_matrix(matrix_type, imp):
	return shunt_admittance_matrix(matrix_type, 1 / imp)
def series_capacitor_matrix(matrix_type, cap, freq):
	return series_impedance_matrix(matrix_type, capacitor_imp(cap, freq))
def shunt_capacitor_matrix(matrix_type, cap, freq):
	return shunt_impedance_matrix(matrix_type, capacitor_imp(cap, freq))
def series_inductor_matrix(matrix_type, ind, freq):
	return series_impedance_matrix(matrix_type, inductor_imp(ind, freq))
def shunt_inductor_matrix(matrix_type, ind, freq):
	return shunt_impedance_matrix(matrix_type, inductor_imp(ind, freq))
def series_resistor_matrix(matrix_type, res):
	return series_impedance_matrix(matrix_type, res)
def shunt_resistor_matrix(matrix_type, res):
	return shunt_impedance_matrix(matrix_type, res)
def series_conductor_matrix(matrix_type, con):
	return series_admittance_matrix(matrix_type, con)
def shunt_conductor_matrix(matrix_type, con):
	return shunt_admittance_matrix(matrix_type, con)
