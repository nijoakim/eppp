# Copyright 2015-2017 Joakim Nilsson
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

_log_level = 0

def set_log_level(log_level):
	"""
	Sets the logging verbosity.

	Args:
		log_level (int): Logging verbosity. A lower value means less logging. (0 is no logging.)
	"""

	global _log_level
	_log_level = log_level

def get_log_level():
	"""
	Returns the logging verbosity.

	Returns:
		int. The current logging verbosity
	"""
	return log_level

def _log(level, msg):
	if level < 1:
		raise Exception('Log level must be at least 1.')
	if _log_level >= level:
		print(msg)
