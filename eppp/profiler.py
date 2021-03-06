# Copyright 2016-2019 Joakim Nilsson
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

# TODO: Arguments to determine what to profile

#=========
# Imports
#=========

# External
import cProfile

# Internal
import eppp
import eppp.calc

#===========
# Profiling
#===========

cProfile.run('eppp.calc.lumped_network(88123, max_num_comps=4, max_rel_error=0)')
