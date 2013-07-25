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

import csv
import os
import numpy as np
import pandas as pd
import re
from collections import defaultdict
from datetime import datetime


# constants:
debug = False

logs_dir = '/Volumes/Spare Partition/LockLogs/week2'
data_file = logs_dir + '/data/dframe.pickle'

in_pattern = re.compile(r'\d{4}-\d{2}-\d{2}T\d{4}.txt', re.I)
in_strptime = '%Y-%m-%dT%H%M.txt'

index_labels = ['pt_record', 'proc_id', 'user_id', 'workstation', 'app', 'activity',
                'first_seen', 'last_seen', 'total_min', 'sec_since_midnight']
data_types = [ ('pt_record', 'S32'),
               ('proc_id', 'u4'),
               ('user_id', 'S32'),
               ('workstation', 'S24'),
               ('app', 'S16'),
               ('activity', 'S128'),
               ('first_seen', 'M8'),
               ('last_seen', 'M8'),
               ('total_min', 'u2'),
               ('sec_since_midnight', 'u2') ]

# set up variables:
dframe = pd.DataFrame(np.zeros(0,dtype=data_types))


def carryover(s,df,ids):
    # see if pd.Series `s` matches any ids in pd.DataFrame `df` from the last run
    for id in ids:
        r = df.iloc[id]
        if (r['pt_record']==s['pt_record'] and
            r['proc_id']==s['proc_id'] and
            r['user_id']==s['user_id'] and
            r['workstation']==s['workstation'] and
            r['app']==s['app'] and
            r['activity']==s['activity'] ):
            return id
    return None


if __name__=="__main__":

    # path prep
    os.chdir(logs_dir)
    destdir = os.path.dirname(data_file)
    if not os.path.exists(destdir): os.makedirs(destdir)

    # read in activity_names lookup
    activity_names = defaultdict(lambda: 'UNKNOWN')
    #activity_names[111111111] = '(none)' #just viewing MR
    with open('../activities.csv', 'rb') as infile:
        reader = csv.reader(infile, delimiter=',', quotechar='"')
        reader.next() #skip header
        for rline in reader:
            activity_names[ int(rline[0]) ] = rline[1] #build dict

    # init empty var
    loggedPrev = []

    # read in data files
    for filename in sorted(os.listdir('.')):
        if in_pattern.match(filename) is not None:

            # get timestamp
            dt = datetime.strptime(filename, in_strptime)
            tstamp = np.datetime64(dt.isoformat())

            # re-init vars
            splitPrev, loggedCur, act_ids = [], [], ['(none)']

            fileobj = open(filename, 'r')
            print "\nFILE:",filename,"started at",datetime.now().strftime("%H:%M:%S")
            for line in fileobj.readlines():
                splitCur = line.split('|')

                # line is starting new subject
                if len(splitCur)==3:
                    act_ids = ['(none)'] #re-init

                # line shows activity_id
                elif len(splitCur)==5 and splitCur[3]!="":
                    act_ids.append(splitCur[3])

                # line gives details on lock holder
                elif len(splitCur)==6:

                    # find our relevant data
                    ptrec = splitCur[0].strip()
                    procid, work = splitCur[5].split('^')[:2]
                    procid = int(procid)
                    userid, secs = splitCur[2].split('^')[:2]
                    secs = int(secs[ secs.find(',')+1 : secs.find('[') ])
                    app = splitCur[1].split(':')[0]
                    if debug: print "\n     ",ptrec,"#"+str(procid),"EMP"+str(userid),work,app,act_ids

                    # check if this is a different lock which means we reset act_ids
                    if (len(splitPrev) > 5) and not ( (splitCur[0]==splitPrev[0]) and
                         (splitCur[1]==splitPrev[1]) and (splitCur[5]==splitPrev[5]) ):
                        act_ids = ['(none)'] #re-init

                    # locks for each activity are separate
                    for act_id in act_ids:

                        # lookup activity name
                        if act_id.isdigit():
                            activity = activity_names[int(act_id)]
                        else:
                            #sometimes this field has a text value
                            activity = act_id

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

                        # see if this line is a carryover from the previous snapshot file
                        result = carryover(row, dframe, loggedPrev)
                        if result!=None: #update duration of existing record
                            record = dframe.iloc[result]
                            record['last_seen'] = tstamp
                            record['total_min'] += 5
                            loggedCur.append(result) #remember it for next file loop
                            if debug: print "      * updated previous record:",result,"for activity:",activity

                        else: #create new record
                            dframe = dframe.append(row, ignore_index=True)
                            last_index = len(dframe)-1 #id for row we just added
                            loggedCur.append(last_index) #remember it for next file loop
                            if debug: print "      * new record:",last_index,"for activity:",activity

                # line is empty
                elif line.strip()=="":
                    continue

                # line format was unexpected
                else:
                    if debug: print 'Unexpected line format: ',line

                # save previous split for comparison
                splitPrev = splitCur

            fileobj.close()
            dframe.save(data_file) #pickle early, pickle often!
            loggedPrev = loggedCur
