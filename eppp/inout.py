# Copyright 2014-2020 Joakim Nilsson
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
import decimal as _dec
import glob    as _glob
import numpy   as _np
from inspect import currentframe as _currentframe
from math import nan, inf

# Internal
from .debug import *

#==========
# Notation
#==========

_default_str_sci_args = {
	'num_sig_figs'   : 4,
	'notation_style' : 'metric',
	'strict_style'   : False,
}

# TODO: Error if invalid kwarg
# TODO: Always print real part of complex numbers if it is non-zero (same with imaginary part)
def set_default_str_sci_args(**kwargs):
	"""
		TODO
	"""
	global _default_str_sci_args
	for name, value in kwargs.items():
		_default_str_sci_args[name] = value

def print_sci(
		x,
		unit           = '',
		name           = None,
		num_sig_figs   = None,
		notation_style = None, # Valid values: 'metric', 'scientific', 'engineering'
		strict_style   = None,
	):
	# TODO: Document all arguments
	"""
	Convert a number to scientific notation and print it.

	Args:
		x (number/str): Number to convert. If a string is given, the variable represented by the string will be used and 'name' will be assigned that string.

	Kwargs:
		name (str): Name of quantity to be printed.
		unit (str): Unit of number to be converted.
	"""

	# Allow specifying 'x' as variable name string
	# This must be done here even if it is done inside 'str_sci' since the local local scope is not visible to callees
	if isinstance(x, str):
		if not name is None:
			raise ValueError("'name' must be None if 'x' is string.")

		context = dict(list(globals().items()) + list(_currentframe().f_back.f_locals.items()))
		if x in context:
			name = x
			x    = context[x]
		else:
			raise ValueError("Variable '%s' does not exist." % x)

	print(
		str_sci(
			x,
			name           = name,
			unit           = unit,
			num_sig_figs   = num_sig_figs,
			notation_style = notation_style,
			strict_style   = strict_style,
		)
	)

# TODO: Special case for percent, permille, ppm, ppb, ppt and ppq?
def str_sci(x,
	unit           = '',
	name           = None,
	num_sig_figs   = None,
	notation_style = None, # Valid values: 'metric', 'scientific', 'engineering'
	strict_style   = None,
):
	# TODO: Document all arguments
	"""
	Convert a number to scientific notation.

	Args:
		x (number/str): Number to convert. If a string is given, the variable represented by the string will be used and 'name' will be assigned that string.

	Kwargs:
		name (str): Name of quantity to be added to resulting string.
		unit (str): Unit of number to be converted.

	Returns:
		str. String representation of the converted number.
	"""

	# Allow specifying 'x' as variable name string
	if isinstance(x, str):
		if not name is None:
			raise ValueError("'name' must be None if 'x' is string.")

		context = dict(list(globals().items()) + list(_currentframe().f_back.f_locals.items()))
		if x in context:
			name = x
			x    = context[x]
		else:
			raise ValueError("Variable '%s' does not exist." % x)

	# Non-prefixable values
	if x ==  inf \
	or x == -inf \
	or x ==  nan:
		return str(x)

	# Round a number to a set number of significant figures
	def convert_sig_figs(x, sig_figs):
		# Minimum amount of significant figures
		if sig_figs < 1:
			raise ValueError('Minimum amount of significant figures is 1.')

		# Convert to set number of significant figures
		highness = int(_np.floor(_np.log10(abs(x))))

		#========================================
		# Return rounded (halves are rounded up)
		#========================================

		# Decimal form (for appropriate rounding method)
		_dec.getcontext().prec = num_sig_figs + 1
		x = _dec.Decimal(x)

		# Decimal shift for appropriate rounding
		# (float multiplication/division unsupported)
		num_shifts = 1 + highness - sig_figs
		if num_shifts < 0:
			x *= int(10**-num_shifts)
		else:
			x /= int(10**num_shifts)

		# Round
		x = x.quantize(_dec.Decimal('1'), rounding=_dec.ROUND_HALF_UP)

		# Shift back
		if num_shifts < 0:
			x /= int(10**-num_shifts)
		else:
			x *= int(10**num_shifts)

		x = float(x) # Back to float
		return x     # Return

	# Logarithms with base (math does not allow bases bigger than 36)
	def log_base_x(x, base):
		return _np.log(x) / _np.log(base)

	# Default arguments
	global _default_str_sci_args
	if num_sig_figs is None:
		num_sig_figs = _default_str_sci_args['num_sig_figs']
	if notation_style is None:
		notation_style = _default_str_sci_args['notation_style']
	if strict_style is None:
		strict_style = _default_str_sci_args['strict_style']

	# Determine the larger of the real and imaginary parts if metric style
	if notation_style == 'metric':
		if x.real == 0 or x.imag == 0:
			larger_xx = abs(x)
		else:
			larger_xx = max(abs(x.real), abs(x.imag))

	# Set number of significant figures for real and imaginary part separately
	original_x = x     # Remember 'x' before converting
	ret_strs   = []    # String representations of real and imaginary part
	has_prefix = False # Whether a prefix for unit has been added
	for xx, complex_postfix in zip((x.real, x.imag), ('', 'j')):
		# Don't convert if 0
		if  xx == 0:
			continue

		# Remove insignificant figures
		xx = convert_sig_figs(xx.real, num_sig_figs)

		# Don't convert if 0 (check this again in case of rounding to 0)
		if  xx == 0:
			continue

		# Notation variables
		if notation_style == 'metric' or notation_style == 'engineering':
			digit_group_size = 3
		elif notation_style == 'scientific':
			digit_group_size = 1
		else:
			raise ValueError('Invalid notation style.')

		# Convert to exponent notation
		xxx          = larger_xx if notation_style == 'metric' else xx
		highness     = int(_np.floor(log_base_x(abs(xxx), 10**digit_group_size)))
		significand  = xx / 10**(highness * digit_group_size)
		exponent     = highness * digit_group_size
		digit_offset = int(_np.floor(_np.log10(abs(significand))))

		# Number of fractional zeroes needed for metric style
		if notation_style == 'metric':
			num_frac_zeros = max(-int(_np.floor(_np.log10(abs(significand)))), 0)
		else:
			num_frac_zeros = 0

		# Convert significand to string
		significand_str = ('%%.%if' % max(0, (num_sig_figs - digit_offset - num_frac_zeros - 1))) % (significand)

		# Do not add to list if 0 after rounding
		if  float(significand_str) == 0:
			continue

		# Add 'j'-postfix if complex
		significand_str = significand_str + complex_postfix

		# Put minus in front of j
		if len(significand_str) > 1 and significand_str[1] == '-':
			significand_str = \
				significand_str[1 ] + \
				significand_str[0 ] + \
				significand_str[2:]

		# Scientific or engineering style
		if notation_style == 'scientific' or notation_style == 'engineering':
			to_append = '%se%i' % (significand_str, exponent)

			# Remove trailing 'e0' if not strict
			if not strict_style:
				if to_append.endswith('e0'):
					to_append = to_append[:-2]

			# Append to return strings list
			ret_strs.append(to_append)

		# Metric style
		elif notation_style == 'metric':
			# Metric prefixes
			PREFIXES = [
				'y', 'z', 'a', 'f', 'p', 'n', 'µ', 'm',
				'',
				'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y',
			]

			# Append to return string list
			ret_strs.append(significand_str)

			# Adjust prefix
			if not has_prefix:
				try:
					index = (exponent + 24) // 3 # (yocto is 1e-24)
					prefix = PREFIXES[index]

					# Treat negative indices as out of bounds
					if index < 0:
						raise IndexError()
				except IndexError: # Out of range for metric
					# Default to engineering style
					return str_sci(
						original_x,
						num_sig_figs   = num_sig_figs,
						notation_style = 'engineering',
						strict_style   = strict_style,
						unit           = unit,
						name           = name,
					)

				# Add prefix to unit
				unit       = prefix + unit
				has_prefix = True

	# Provoke error which was missed in case of x = 0
	convert_sig_figs(1, num_sig_figs)

	# Default operator is plus
	operator_str = '+'

	# Return 0 with correct significant figures ('convert_sig_figs()' does not work with x = 0)
	if len(ret_strs) == 0:
		if num_sig_figs == 1:
			ret = '0'
		else:
			ret = '0.' + '0'*(num_sig_figs - 1)
	
	# Otherwise, assemble string normally
	else:
		# Use minus as operator for beauty if applicable
		if len(ret_strs) == 2:
			if ret_strs[1][0] == '-':
				ret_strs[1] = ret_strs[1][1:]
				operator_str = '-'

		# Assemble string
		ret = (' %s ' % operator_str).join(ret_strs)

		# Parenthesize if complex
		if len(ret_strs) == 2:
			ret = '('+ ret +')'

	# Add unit
	if unit != '':
		ret += ' '+ unit

	# Add quantity name
	if not name is None:
		ret = '%s =\n\t%s' % (name, ret)

	return ret

#===========
# Read data
#===========

EXT_GNUCAP     = 1
EXT_ARCHIMEDES = 2

def read_data(fmt, path):
	"""
	TODO: Documentation
	"""
	if (fmt == EXT_GNUCAP    ): return _read_gnucap(path)
	if (fmt == EXT_ARCHIMEDES): return _read_archimedes(path)
	raise Exception("Invalid format")

# TODO: Bug for empty data set
def _read_gnucap(path):
	"""
	Reads a gnucap file and returns a dictionary with its contents.

	Args:
		path (str): Path to file to read.

	Returns:
		dict. Dictionary containing numpy.ndarrays of the read data 
	"""

	# Read data
	names=[]
	with open(path, 'r') as f:
		names    = f.readline().split()
		names[0] = names[0][1:] # Remove initial '#'
	data = _np.genfromtxt(path)

	# Put data in dictionary
	ret_dict = {}
	try:
		for i in range(data.shape[1]):
			ret_dict[names[i]] = data[0:, i]
	except IndexError: # Catch array shape error when data is of length 1
		for i in range(data.shape[0]):
			ret_dict[names[i]] = _np.array([data[i]])

	return ret_dict

def _read_archimedes(path):
	# Get relevant paths
	files = _glob.glob(path + "/*.xyz")

	# Generate dictionary of dictionaries
	# Outer dictionary key is filename.
	# Inner dictionary keys are 'x', 'y' and 'mag'
	dict_outer = {}
	for f in files:
		# Get the data
		data = _np.genfromtxt(f)

		# Reshape the data so it can be extracted more easily
		new_shape = data.shape
		new_shape = (new_shape[1], new_shape[0])
		data = data.reshape((1, new_shape[0] * new_shape[1]), order = 'C')
		data = data.reshape(new_shape, order = 'F')

		# Get data
		dict_inner = {}
		dict_inner['x']   = data[0]
		dict_inner['y']   = data[1]
		dict_inner['mag'] = data[2]

		# Cut directory part of path and file extension
		property_name = f[f.rfind('/') + 1 : f.rfind('.')]

		# Assign inner dictionary to outer one
		dict_outer[property_name] = dict_inner

	# Return dictionary of dictionaries
	return dict_outer

#============
# Annotation
#============
# TODO: Should annotation really be a part of eppp? In that case, can it be made more general?

class _TextFields:
	# 'color' constants
	COLOR_BACKGROUND         = 0
	COLOR_PIN                = 1
	COLOR_NET_ENDPOINT       = 2
	COLOR_GRAPHIC            = 3
	COLOR_NET                = 4
	COLOR_ATTRIBUTE          = 5
	COLOR_LOGIC_BUBBLE       = 6
	COLOR_GRID_POINT         = 7
	COLOR_DETACHED_ATTRIBUTE = 8
	COLOR_TEXT               = 9
	COLOR_BUS                = 10
	COLOR_SELECTION          = 11
	COLOR_BOUNDING_BOX       = 12
	COLOR_ZOOM_BOX           = 13
	COLOR_STROK              = 14
	COLOR_LOCK               = 15
	COLOR_NET_JUNCTION       = 16
	COLOR_MESH_GRID_MINOR    = 17
	COLOR_MESH_GRID_MAJOR    = 18

	# 'visibility constants'
	VISIBILITY_INVISIBLE = 0
	VISIBILITY_VISIBLE   = 1

	# 'show_name_value' constants
	SHOW_NAME_VALUE = 0
	SHOW_VALUE      = 1
	SHOW_NAME       = 2

	# 'alignment' constants
	ALIGNMENT_HOR_LEFT   = -1
	ALIGNMENT_HOR_CENTER =  0
	ALIGNMENT_HOR_RIGHT  =  1
	ALIGNMENT_VER_BOTTOM = -1
	ALIGNMENT_VER_MIDDLE =  0
	ALIGNMENT_VER_TOP    =  1

	def __init__(self, tLine):
		fields = tLine.split()
		self.x               = int(fields[1])
		self.y               = int(fields[2])
		self.color           = int(fields[3])
		self.size            = int(fields[4])
		self.visibility      = int(fields[5])
		self.show_name_value = int(fields[6])
		self.angle           = int(fields[7])
		self.alignment_hor   = int(fields[8]) / 3 - 1
		self.alignment_ver   = int(fields[8]) % 3 - 1
		self.numLines        = int(fields[9])

	def __str__(self):
		return 'T '+ str.join(' ', map(str, [
			int(self.x),
			int(self.y),
			self.color,
			self.size,
			self.visibility,
			self.show_name_value,
			self.angle,
			int((self.alignment_hor + 1)*3 + self.alignment_ver + 1),
			self.numLines,
		]))

	# TODO: angle
	# TODO: What to do for center / middle alignment???? raise exception?
	def move_along_orientation(self, dx, dy):
		self.x += dx * self.alignment_hor
		self.y += dy * self.alignment_ver

	def move_along_orientation_scaled(self, dx, dy):
		factor = 20 * self.size
		self.move_along_orientation(factor*dx, factor*dy)

# TODO: Error handling
# TODO: Code reuse for 'netname' / 'refdes'
# TODO: Possible to automatically calculate transconductance and other parameters?
def annotate_gschem(fn_in, fnd_out, data, index = 0):
	"""
		TODO: Document when more complete!
	"""
	cur_text_fields = None
	cur_id = ''
	cur_match = 'none'
	with open(fn_in, 'r') as fIn:
		with open(fnd_out, 'w') as f_out:
			for line in fIn.readlines():
				# Copy line from input file
				f_out.write(line)

				# Match non-'}'
				if cur_match == 'none':
					# Match text field
					cur_match_str = 'T'
					if line.startswith(cur_match_str):
						cur_text_fields = _TextFields(line) # Get cur_text_fields

					# Match net name
					cur_match_str = 'netname'
					if line.startswith(cur_match_str):
						cur_id = line[len(cur_match_str) + 1 : -1] # Get net name
						if 'v('+ cur_id +')' in data:
							cur_match = cur_match_str

					# Match reference designator
					cur_match_str = 'refdes'
					if line.startswith(cur_match_str):
						cur_id = line[len(cur_match_str) + 1 : -1] # Get net name
						if 'i('+ cur_id +')' in data:
							cur_match = cur_match_str

				# Match '}'
				else:
					cur_match_str = '}'
					if line.startswith(cur_match_str):
						# If last match was 'netname'
						if cur_match == 'netname':
							# Modify text fields
							cur_text_fields.move_along_orientation_scaled(0, 1)          # Position
							cur_text_fields.size -= 2                                    # Font size
							cur_text_fields.color = _TextFields.COLOR_DETACHED_ATTRIBUTE # Color
							
							# Write new text
							f_out.write(str(cur_text_fields) +'\n')
							f_out.write(str_sci(data['v('+ cur_id +')'][index], unit='V') + '\n')

						if cur_match == 'refdes':
							# Modify text fields
							cur_text_fields.move_along_orientation_scaled(0, -1)         # Position
							cur_text_fields.size -= 2                                    # Font size
							cur_text_fields.color = _TextFields.COLOR_DETACHED_ATTRIBUTE # Color

							# Write new text
							f_out.write(str(cur_text_fields) +'\n')
							f_out.write(str_sci(data['i('+ cur_id +')'][index], unit='A') + '\n')

						# Reset current match
						cur_match = 'none'
