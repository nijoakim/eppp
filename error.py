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

_supress_exceptions = False

def exceptions_on():
	global _supress_exceptions
	_supress_exceptions = False


def exceptions_off():
	global _supress_exceptions
	_supress_exceptions = True

# Dynamic docstring generation
def _doc_exceptions(on_off_str):
	return """
		Turns exceptions %s for this module. When exceptions are on, functions in this module are able to raise exceptions. When they are off, exceptions are suppressed when they occur and instead a warning message is printed.
	""" % on_off_str
exceptions_on.__doc__  = _doc_exceptions('on')
exceptions_off.__doc__ = _doc_exceptions('off')

def _string_or_exception(msg):
	global _supress_exceptions
	if _supress_exceptions:
		return 'Warning: '+ msg
	else:
		raise Exception(msg)
