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

_supressExceptions = False

def exceptionsOn():
	global _supressExceptions
	_supressExceptions = False


def exceptionsOff():
	global _supressExceptions
	_supressExceptions = True

# Dynamic docstring generation
def _docExceptions(onOffStr):
	return '''
		Turns exceptions %s for this module. When exceptions are on, functions in this module are able to raise exceptions. When they are off, exceptions are suppressed when they occur and instead a warning message is printed.
	''' % onOffStr
exceptionsOn.__doc__  = _docExceptions("on")
exceptionsOff.__doc__ = _docExceptions("off")

def _stringOrException(msg):
	global _supressExceptions
	if _supressExceptions:
		return "Warning: "+ msg
	else:
		raise Exception(msg)
