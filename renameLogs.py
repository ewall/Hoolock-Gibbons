#!/usr/bin/env python
'''
Hoolock-Gibbons/renameLogs.py:
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


Purpose: simply renaming files so they are sortable by timestamp

example input filename:  "2013_Jul_1_(0001).txt"
desired output filename: "2013-07-01T0001.txt"

'''

import os
import re
from datetime import datetime

in_pattern = re.compile(r'\d{4}_\w{3}_\d{1,2}_\(\d{4}\).txt', re.I)
in_strptime = '%Y_%b_%d_(%H%M).txt'
out_strptime = '%Y-%m-%dT%H%M.txt'

os.chdir('./logs')

for filename in os.listdir('.'):
    if in_pattern.match(filename) is not None:
        tstamp = datetime.strptime(filename, in_strptime)
        new_filename = tstamp.strftime(out_strptime)
        print "{0} --> {1}".format(filename, new_filename)
        os.rename(filename, new_filename)
