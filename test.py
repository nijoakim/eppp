# Copyright 2015 Joakim Nilsson
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

# from eppp import *
from __init__ import *
import debug as _dbg
import inout as _inout

set_log_level(0)

# Lumped find tests
import time
import cProfile

# t = time.time()
bc = lumped_network(88123, max_num_comps = 3)
cProfile.run('lumped_network(88123, max_num_comps = 3)')
# _dbg.printVar(time.time() - t, 'time')
from calc_lumped_network import _polish_eval
# print(_polish_eval(bc))
print(bc)
