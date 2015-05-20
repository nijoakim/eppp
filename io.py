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
import glob as _glob
from error import _stringOrException

#==========
# Notation
#==========

_defaultSigFigs = 4

def setDefaultSigFigs(sigFigs):
	"""
	Sets the default value for the number of significant figures to use during conversion to scientific notation with 'strSci' and 'printSci'.
	
	Args:
		sigFigs: New default value for number of significant figures.
	"""
	global _defaultSigFigs
	_defaultSigFigs = sigFigs

def strSci(x, unit = '', sigFigs = _defaultSigFigs):
	# Limit to at least 3 significant figures
	if sigFigs < 3:
		_stringOrException('Minimum allowable value for significant figures is 3.')
		sigFigs = 3
	
	# Consider only positive numbers
	signX = _pl.sign(x)
	x *= signX
	
	# Prefixes
	PREFIXES = ['y', 'z', 'a', 'f', 'p', 'n', 'u', 'm', '', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'] # Metric prefixes
	x *= 1.e24                                                                                      # Largest prefix multiplier
	
	# Adjust 'x' and find prefix
	i = min( int(_pl.log10(x)), (len(PREFIXES) - 1)*3 )
	prefix = PREFIXES[i/3]
	x = round(x, -i - 1 + sigFigs)
	x /= 1e3**(i/3)
	
	return ('%.'+ str(sigFigs - 1 - i%3) +'f') % (x*signX) +' '+ prefix + unit

def printSci(x, unit = '', sigFigs = _defaultSigFigs):
	print(strSci(x, unit = unit, sigFigs = sigFigs))

# Dynamic docstring generation
def _docSci(printAlso):
	return '''
		Convert a number to scientific notation%s.
		
		Args:
			x (number): Number to convert
		
		Kwargs:
			unit (str): Unit of number to be converted%s
	''' % (
		' and print it' if printAlso else '',
		'''
		
		Returns:
			str. String representation of the converted number.
		''' if not printAlso else ''
	)
strSci.__doc__   = _docSci(False)
printSci.__doc__ = _docSci(True)

#===========
# Read data
#===========

EXT_GNUCAP     = 1
EXT_ARCHIMEDES = 2

# TODO: Privatize sub functions
def readData(fmt, path):
	if (fmt == EXT_GNUCAP    ): return readGnucap(path)
	if (fmt == EXT_ARCHIMEDES): return readArchimedes(path)
	raise Exception("Invalid format")

# TODO: Bug for empty data set
def readGnucap(path):
	'''
	Reads a gnucap file and returns a dictionary with its contents.
	
	Args:
		path (str): Path to file to read.
	
	Returns:
		dict. Dictionary containing numpy.ndarrays of the read data 
	'''
	
	# Read data
	names=[]
	with open(path, 'r') as f:
		names = f.readline().split()
		names[0] = names[0][1:] # Remove initial '#'
	data = _pl.genfromtxt(path)
	
	# Put data in dictionary
	retDict = {}
	try:
		for i in range(data.shape[1]):
			retDict[names[i]] = data[0:, i]
	except IndexError: # Catch array shape error when data is of length 1
		for i in range(data.shape[0]):
			retDict[names[i]] = _pl.np.array([data[i]])
	
	return retDict

def readArchimedes(path):
	# Get relevant paths
	files =_glob.glob(path + "/*.xyz")
	
	dictOuter = {}
	for f in files:
		data = _pl.genfromtxt(f)
		
		newShape = data.shape
		newShape = (newShape[1], newShape[0])
		data = data.reshape((1, newShape[0] * newShape[1]), order = 'C')
		data = data.reshape(newShape, order = 'F')
		
		dictInner = {}
		dictInner['x']   = data[0]
		dictInner['y']   = data[1]
		dictInner['mag'] = data[2]
		
		propertyName = f[4 : -4] # TODO: Do properly
		dictOuter[propertyName] = dictInner
	
	return dictOuter
	

#============
# Annotation
#============

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
		self.x             = int(fields[1])
		self.y             = int(fields[2])
		self.color         = int(fields[3])
		self.size          = int(fields[4])
		self.visibility    = int(fields[5])
		self.showNameValue = int(fields[6])
		self.angle         = int(fields[7])
		self.alignmentHor  = int(fields[8]) / 3 - 1
		self.alignmentVer  = int(fields[8]) % 3 - 1
		self.numLines      = int(fields[9])
	
	def __str__(self):
		return 'T '+ str.join(' ', map(str, [
			self.x,
			self.y,
			self.color,
			self.size,
			self.visibility,
			self.showNameValue,
			self.angle,
			(self.alignmentHor + 1)*3 + self.alignmentVer + 1,
			self.numLines
		]))
	
	# TODO: angle
	# TODO: What to do for center / middle alignment???? raise exception?
	def moveAlongOrientation(self, dx, dy):
		self.x += dx * self.alignmentHor
		self.y += dy * self.alignmentVer
	
	def moveAlongOrientationScaled(self, dx, dy):
		factor = 20 * self.size
		self.moveAlongOrientation(factor*dx, factor*dy)

# TODO: Error handling
# TODO: Code reuse for 'netname' / 'refdes'
# TODO: Possible to automatically calculate transconductance and other parameters?
def annotateGschem(fnIn, fnOut, data, index = 0):
	"""
		TODO: Document when more complete!
	"""
	curTextFields = None
	curId = ''
	curMatch = 'none'
	with open(fnIn, 'r') as fIn:
		with open(fnOut, 'w') as fOut:
			for line in fIn.readlines():
				# Copy line from input file
				fOut.write(line)
				
				# Match non-'}'
				if curMatch == 'none':
					# Match text field
					curMatchStr = 'T'
					if line.startswith(curMatchStr):
						curTextFields = _TextFields(line) # Get curTextFields
				
					
					# Match net name
					curMatchStr = 'netname'
					if line.startswith(curMatchStr):
						curId = line[len(curMatchStr) + 1 : -1] # Get net name
						if 'v('+ curId +')' in data:
							curMatch = curMatchStr
					
					# Match reference designator
					curMatchStr = 'refdes'
					if line.startswith(curMatchStr):
						curId = line[len(curMatchStr) + 1 : -1] # Get net name
						if 'i('+ curId +')' in data:
							curMatch = curMatchStr
				
				# Match '}'
				else:
					curMatchStr = '}'
					if line.startswith(curMatchStr):
						# If last match was 'netname'
						if curMatch == 'netname':
							# Modify text fields
							curTextFields.moveAlongOrientationScaled(0, 1)             # Position
							curTextFields.size -= 2	                                   # Font size
							curTextFields.color = _TextFields.COLOR_DETACHED_ATTRIBUTE # Color
							
							# Write new text
							fOut.write(str(curTextFields) +'\n')
							fOut.write(strSci(data['v('+ curId +')'][index], 'V') + '\n')
						
						if curMatch == 'refdes':
							# Modify text fields
							curTextFields.moveAlongOrientationScaled(0, -1)            # Position
							curTextFields.size -= 2	                                   # Font size
							curTextFields.color = _TextFields.COLOR_DETACHED_ATTRIBUTE # Color
							
							# Write new text
							fOut.write(str(curTextFields) +'\n')
							fOut.write(strSci(data['i('+ curId +')'][index], 'A') + '\n')
						
						# Reset current match
						curMatch = 'none'
