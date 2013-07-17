#!/usr/bin/env python
'''
Hoolock-Gibbons/importLogs.py:
Copyright 2013 Eric W. Wallace / MaineHealth

This file is part of Hoolock-Gibbons.

Hoolock-Gibbons is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Hoolock-Gibbons is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Hoolock-Gibbons.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import numpy as np
import pandas as pd

os.chdir('./logs')

for filename in sort(os.listdir('.')):
    