# Copyright 2014-2017 Joakim Nilsson
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

# Version
__version__ = '0.1.0'

# Docstring
"""
Electronics in python.
TODO: Document properlier!
"""

#=========
# Imports
#=========

# Import everything into root module
from .calc  import *
from .inout import *
from .log   import *
from .plot  import *

# Delete sub-modules
del calc
del inout
del log
del plot

# Private external
import types as _t

# Private internal
from . import calc  as _calc
from . import inout as _inout
from . import log   as _log
from . import plot  as _plot

#===================================================
# Linebreak long lines in all functions' docstrings
#===================================================

# Function to do this
def _format_doc_strings(modules, width, indent):
	completed = []
	for module in modules:
		for attr_str in dir(module):
			attr = getattr(module, attr_str)
			if isinstance(attr, _t.FunctionType) \
			and hasattr(attr, '__doc__') \
			and not attr.__doc__ is None \
			and not attr in completed:
				completed.append(attr)
				doc = attr.__doc__
				doc = doc.expandtabs(indent)
				lines = doc.split('\n')
				lines.reverse() # Reverse iteration improves list efficiency from O(n) to O(1)
				doc = ''
				new = True
				while len(lines) > 0:
					# Indent
					if new:
						cur_indent = lines[-1].find(':') + 1
						cur_indent += len(lines[-1][cur_indent:]) - len(lines[-1][cur_indent:].lstrip(' ')) + indent
						new = False
						new_width = width
					else:
						doc += ' '*cur_indent
						new_width = width - cur_indent

					# Word wrap
					if len(lines[-1]) > new_width:
						break_index = lines[-1].rfind(' ', 0, new_width)
						doc += lines[-1][0 : break_index]
						lines[-1] = lines[-1][break_index + 1 :]
					else:
						doc += lines.pop(-1)
						new = True
					doc += '\n'
				attr.__doc__ = doc

# Call the function
_format_doc_strings([_calc, _inout, _log, _plot], 79, 4)
