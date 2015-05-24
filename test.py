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

setLogLevel(2)

# Tests
import time
t = time.time()
# print(getAvailVals('E6', compType = 'capacitor', freq = 1))
bc = lumpedNetwork(1/88123j, maxRelError = 0.01, availVals = getAvailVals('E6', compType = 'capacitor', freq = 1))
# bc = lumpedNetwork(88123, maxRelError = 0.01)
# bc = lumpedNetwork(1025, maxNumComps = 3, availVals = [50, 1000], maxAbsError = 0)
_dbg.printVar(time.time() - t, 'time')
print(bc)
from util import _polishEval
print(_polishEval(bc))

