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

###########################################################################
### NOTE: This file may not be useful run as a "normal" Python script;  ###
### it is more a collection of notes for browsing the stats in iPython. ###
###########################################################################
'''

import os
import numpy as np
import pandas as pd
from datetime import datetime


# REFERENCE:
# data_types = [ ('pt_record', 'S32'),
#                ('proc_id', 'u4'),
#                ('user_id', 'S32'),
#                ('workstation', 'S24'),
#                ('app', 'S16'),
#                ('activity', 'S128'),
#                ('first_seen', 'M8'),
#                ('last_seen', 'M8'),
#                ('total_min', 'u2'),
#                ('sec_since_midnight', 'u2') ]


# Medical Records:
mr = dframe[dframe.app=="MR"]

# TODO:
# - basic stats on total_minutes: avg, max, mean
# - common workflows: group by activity, count locks, get top
#   - group by activity, sum times, get top
#   - corr/cov between activities, so we know which are more likely to effect others?
# - "slowest" users: group by user, average times, get outliers & compare with averages
# - "sticky" workstations: group by workstation, average times, get outliers


# Other Apps:
other = dframe[dframe.app!="MR"]

# - should these be compared against the MR locks? e.g. does REG lock out MR?
# - any use in comparing these against each other?


# External Info:
# - any value in extracting user's departments?
# - what about dividing into 3 shifts (based on secs_since_midnight)?
#   - might that tell us which need more training
#   - interesting to see locks which overlap the shift change

# LEARN:
# - ¡most important! is when 2 users are trying to view the same patient at the same time -- how to do this???
