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
import re
from datetime import datetime

# constants:
debug = True
in_pattern = re.compile(r'\d{4}-\d{2}-\d{2}T\d{4}.txt', re.I)
in_strptime = '%Y-%m-%dT%H%M.txt'

index_labels = ['pt_record', 'proc_id', 'user_id', 'workstation', 'app', 'activity', 
                'first_seen', 'last_seen', 'total_min', 'sec_since_midnight']
data_types = [ ('pt_record', 'u4'),
               ('proc_id', 'u4'),
               ('user_id', 'u4'),
               ('workstation', 'S32'),
               ('app', 'S16'),
               ('activity', 'u2'),
               ('first_seen', 'M8'),
               ('last_seen', 'M8'),
               ('total_min', 'u2'),
               ('sec_since_midnight', 'u2') ]

# set up variables:
dframe = pd.DataFrame(np.zeros(0,dtype=data_types))

# start:
os.chdir('F:/dev/Hoolock-Gibbons/logs') #change back!

for filename in sorted(os.listdir('.')):
    if in_pattern.match(filename) is not None:
        
        # get timestamp
        dt = datetime.strptime(filename, in_strptime)
        tstamp = np.datetime64(dt.isoformat()) 
        
        # init empty vars
        splitPrev, act_ids, loggedCur, loggedPrev = [], [], [], []
        #?
        
        fileobj = open(filename, 'r')
        if debug: print "FILE:",filename
        for line in fileobj.readlines():
            splitCur = line.split('|')
            
            # line is starting new subject
            if len(splitCur)==3:
                splitPrev, act_ids = splitCur, []
                if debug: print 'reset'
                continue
                
            # line shows activity_id
            elif len(splitCur)==5 and splitCur[3]!="":       
                act_ids.append(splitCur[3])
                if debug: print 'activity'
                continue
            
            # line gives details on lock holder
            elif len(splitCur)==6:
                if debug: print 'details'
                
                # locks for each activity are separate
                if act_ids==[]: act_ids = [""] #empty is valid
                for act_id in act_ids:
                
                    # TODO: lookup activity name
                    #activity = activities[act_id]
                    activity = "unknown"
                    
                    # find our relevant data
                    ptrec = splitCur[0].strip(' Z')
                    procid, work = splitCur[5].split('^')[:2]
                    userid, secs = splitCur[2].split('^')[:2]
                    secs = secs[ secs.find(',')+1 : secs.find('[') ]
                    app = splitCur[1].split(':')[0]
                    
                    # create data row
                    row = pd.Series({ 'pt_record': ptrec,
                                      'proc_id': procid,
                                      'user_id': userid,
                                      'workstation': work,
                                      'app': app,
                                      'activity': activity,
                                      'first_seen': tstamp,
                                      'last_seen': tstamp,
                                      'total_min': 1,
                                      'sec_since_midnight': secs })
                    
                    # TODO: call carryover func
                    #if carryover returns id, edit it
                    
                    #else new record
                    dframe = dframe.append(row, ignore_index=True)
                    last_index = len(dframe)-1 #id for row we just added
                    loggedCur.append(last_index) #remember it for next file loop
                        
            # line is empty
            elif line.strip()=="":
                continue
        
            # line format was unexpected
            else:
                print 'Unexpected line format: ',line
                continue
        
        fileobj.close()
        loggedPrev = loggedCur