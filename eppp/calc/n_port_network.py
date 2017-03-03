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

	# TODO: Errors instead of asserts
	if not 'z' in (from_, to):
		matrix = convert_parameter_matrix(matrix, from_, 'z') # Convert to z-parameters
		matrix = convert_parameter_matrix(matrix, 'z',   to)  # Convert to 'to'-parameters
		return matrix

	# Symmetric conversions
	if   'y' in (from_, to):
		return _np.linalg.inv(matrix)
	elif 'h' in (from_, to):
		assert matrix.shape == (2, 2)
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = _np.linalg.det(matrix)
		matrix_out[0][1] = matrix[0][1]
		matrix_out[1][0] = -matrix[1][0]
		matrix_out[1][1] = 1
		matrix_out /= matrix[1][1]
		return matrix_out
	elif 'g' in (from_, to):
		assert matrix.shape == (2, 2)
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = 1
		matrix_out[0][1] = -matrix[0][1]
		matrix_out[1][0] = matrix[1][0]
		matrix_out[1][1] = _np.linalg.det(matrix)
		matrix_out /= matrix[0][0]
		return matrix_out
	elif 'a' in (from_, to):
		assert matrix.shape == (2, 2)
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = matrix[0][0]
		matrix_out[0][1] = _np.linalg.det(matrix)
		matrix_out[1][0] = 1
		matrix_out[1][1] = matrix[1][1]
		matrix_out /= matrix[1][0]
		return matrix_out

	# Asymmetric conversions
	if   (from_, to) == ('z', 'b'):
		assert matrix.shape == (2, 2)
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = matrix[1][1]
		matrix_out[0][1] = -_np.linalg.det(matrix)
		matrix_out[1][0] = -1
		matrix_out[1][1] = matrix[0][0]
		matrix_out /= matrix[0][1]
		return matrix_out
	elif (from_, to) == ('b', 'z'):
		assert matrix.shape == (2, 2)
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = -matrix[1][1]
		matrix_out[0][1] = -1
		matrix_out[1][0] = -_np.linalg.det(matrix)
		matrix_out[1][1] = -matrix[0][0]
		matrix_out /= matrix[1][0]
		return matrix_out

	raise NotImplementedError()

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
