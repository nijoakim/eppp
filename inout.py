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

# TODO: Rename this module! It conflicts with the standard library.

import pylab as _pl
import glob  as _glob
from error import _string_or_exception

#==========
# Notation
#==========

_default_sig_figs = 4

def set_default_sig_figs(sig_figs):
	"""
	Sets the default value for the number of significant figures to use during conversion to scientific notation with 'str_sci' and 'print_sci'.
	
	Args:
		sig_figs: New default value for number of significant figures.
	"""
	global _default_sig_figs
	_default_sig_figs = sig_figs

def str_sci(x, unit = '', sig_figs = None):
	# Default number of significant figures
	if sig_figs is None:
		sig_figs = _default_sig_figs
	
	# Limit to at least 3 significant figures
	if sig_figs < 3:
		print(_string_or_exception('Minimum allowable value for significant figures is 3.'))
		sig_figs = 3
	
	# Consider only positive numbers
	sign_x = _pl.sign(x)
	x *= sign_x
	
	# Prefixes
	PREFIXES = ['y', 'z', 'a', 'f', 'p', 'n', 'u', 'm', '', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'] # Metric prefixes
	x *= 1.e24                                                                                      # Largest prefix multiplier
	
	# Adjust 'x' and find prefix
	i       = min(int(_pl.log10(x)), (len(PREFIXES) - 1)*3)
	prefix  = PREFIXES[i//3]
	x       = round(x, -(i + 1) + sig_figs)
	x      /= 1e3**(i//3)
	
	# Add prefix and unit
	ret = ('%.'+ str(sig_figs - 1 - i%3) +'f') % (x*sign_x)
	if prefix + unit:
		ret += ' '+ prefix + unit
	
	return ret

def print_sci(x, unit = '', sig_figs = _default_sig_figs):
	print(str_sci(x, unit = unit, sig_figs = sig_figs))

# Dynamic docstring generation
def _docSci(printAlso):
	return """
		Convert a number to scientific notation%s.
		
		Args:
			x (number): Number to convert
		
		Kwargs:
			unit (str): Unit of number to be converted%s
	""" % (
		' and print it' if printAlso else '',
		"""
		
		Returns:
			str. String representation of the converted number.
		""" if not printAlso else ''
	)
str_sci.__doc__   = _docSci(False)
print_sci.__doc__ = _docSci(True)

#===========
# Read data
#===========

EXT_GNUCAP     = 1
EXT_ARCHIMEDES = 2

# TODO: Privatize sub functions
def read_data(fmt, path):
	if (fmt == EXT_GNUCAP    ): return read_gnucap(path)
	if (fmt == EXT_ARCHIMEDES): return read_archimedes(path)
	raise Exception("Invalid format")

# TODO: Bug for empty data set
def read_gnucap(path):
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
	data = _pl.genfromtxt(path)
	
	# Put data in dictionary
	ret_dict = {}
	try:
		for i in range(data.shape[1]):
			ret_dict[names[i]] = data[0:, i]
	except IndexError: # Catch array shape error when data is of length 1
		for i in range(data.shape[0]):
			ret_dict[names[i]] = _pl.np.array([data[i]])
	
	return ret_dict

def read_archimedes(path):
	# Get relevant paths
	files = _glob.glob(path + "/*.xyz")
	
	# TODO: Comment, idiot!
	dict_outer = {}
	for f in files:
		data = _pl.genfromtxt(f)
		
		new_shape = data.shape
		new_shape = (new_shape[1], new_shape[0])
		data = data.reshape((1, new_shape[0] * new_shape[1]), order = 'C')
		data = data.reshape(new_shape, order = 'F')
		
		dict_inner = {}
		dict_inner['x']   = data[0]
		dict_inner['y']   = data[1]
		dict_inner['mag'] = data[2]
		
		propertyName = f[4 : -4] # TODO: Do properly
		dict_outer[propertyName] = dict_inner
	
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
			self.x,
			self.y,
			self.color,
			self.size,
			self.visibility,
			self.show_name_value,
			self.angle,
			(self.alignment_hor + 1)*3 + self.alignment_ver + 1,
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
							cur_text_fields.move_along_orientation_scaled(0, 1)             # Position
							cur_text_fields.size -= 2	                                   # Font size
							cur_text_fields.color = _TextFields.COLOR_DETACHED_ATTRIBUTE # Color
							
							# Write new text
							f_out.write(str(cur_text_fields) +'\n')
							f_out.write(str_sci(data['v('+ cur_id +')'][index], 'V') + '\n')
						
						if cur_match == 'refdes':
							# Modify text fields
							cur_text_fields.move_along_orientation_scaled(0, -1)            # Position
							cur_text_fields.size -= 2	                                   # Font size
							cur_text_fields.color = _TextFields.COLOR_DETACHED_ATTRIBUTE # Color
							
							# Write new text
							f_out.write(str(cur_text_fields) +'\n')
							f_out.write(str_sci(data['i('+ cur_id +')'][index], 'A') + '\n')
						
						# Reset current match
						cur_match = 'none'
