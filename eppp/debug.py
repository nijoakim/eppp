# Copyright 2015-2019 Joakim Nilsson
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

# TODO: Can local contexts be automated by getting caller's locals()?
def print_var(var, custom_name = None):
	import inspect

	# Get global and caller's local variables (the latter overrides the former)
	context = dict(list(globals().items()) + list(inspect.currentframe().f_back.f_locals.items()))

	if (custom_name == None):
		# Print name
		notFound = True
		for name in context:
			if context[name] is var:
				print(name)
				notFound = False
				break

		# Print unknown name
		if notFound:
			print('?expression?')
	else:
		print(custom_name)

	# Print value
	print('\t= %s' % str(var))
