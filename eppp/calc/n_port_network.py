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
	# TODO: Verifiy definition
	if   (from_, to) == ('z', 'b'):
		assert matrix.shape == (2, 2)
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = matrix[1][1]
		matrix_out[0][1] = -_np.linalg.det(matrix)
		matrix_out[1][0] = -1
		matrix_out[1][1] = matrix[1][1]
		matrix_out /= matrix[0][1]
		return matrix_out
	elif (from_, to) == ('b', 'z'):
		assert matrix.shape == (2, 2)
		matrix_out       = _np.ndarray((2, 2), dtype=matrix.dtype)
		matrix_out[0][0] = -matrix[1][1]
		matrix_out[0][1] = -1
		matrix_out[1][0] = -_np.linalg.det(matrix)
		matrix_out[1][1] = -matrix[1][1]
		matrix_out /= matrix[1][0]
		return matrix_out

	raise NotImplementedError()
