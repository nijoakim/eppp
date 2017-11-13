#!/usr/bin/env python3

# Copyright 2016 Joakim Nilsson
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

from distutils.core import setup, Extension

fast_misc_module = Extension(
	'eppp/fast_misc',
	sources            = ['eppp/fast_misc.c'],
	extra_compile_args = ['-O3'],
	extra_link_args    = ['-O3'],
)

setup(
	name         = 'eppp',
	version      = '0.1.0',
	author       = 'Joakim Nilsson',
	author_email = 'nijoakim@gmail.com',
	ext_modules  = [fast_misc_module],
	packages     = [
			'eppp',
			'eppp.calc',
	],
)
