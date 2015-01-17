# Copyright 2014 Joakim Nilsson
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

#===============
# Documentation
#===============

# Docstring
"""
Electronics in python.
TODO: Document properlier!
"""

#=========
# Imports
#=========

# Imports
from calc  import *
from error import *
from io    import *
from plot  import *

# Delete sub-imports (put all functions in the same namespace)
del calc
del error
del io
del plot

#===================================================
# Linebreak long lines in all functions' docstrings
#===================================================

# Private imports
import types as _t

# Referencable private imports
import calc  as _calc
import error as _error
import io    as _io
import plot  as _plot

# Function to do this
def _formatDocStrings(modules, width, indent):
	completed = []
	for module in modules:
		for attrStr in dir(module):
			attr = getattr(module, attrStr)
			if isinstance(attr, _t.FunctionType) \
			and hasattr(attr, '__doc__') \
			and not isinstance(attr.__doc__, _t.NoneType) \
			and not attr in completed:
				completed.append(attr)
				doc = attr.__doc__
				doc = doc.expandtabs(indent)
				lines = doc.split('\n')
				lines.reverse() # Going in reverse improves list efficiency from O(n) to O(1)
				doc = ''
				new = True
				while len(lines) > 0:
					# Indent
					if new:
						curIndent = lines[-1].find(':') + 1
						curIndent += len(lines[-1][curIndent:]) - len(lines[-1][curIndent:].lstrip(' ')) + indent
						new = False
						newWidth = width
					else:
						doc += ' '*curIndent
						newWidth = width - curIndent
					
					# Word wrap
					if len(lines[-1]) > newWidth:
						breakIndex = lines[-1].rfind(' ', 0, newWidth)
						doc += lines[-1][0 : breakIndex]
						lines[-1] = lines[-1][breakIndex + 1 :]
					else:
						doc += lines.pop(-1)
						new = True
					doc += '\n'
				attr.__doc__ = doc

# Call the function
_formatDocStrings([_calc, _error, _io, _plot], 79, 4)
