NOTES
=====

These are my random notes as I'm working thru the data and figuring out how to process it.


LOG ANALYSIS
------------

### sample progression:

1st log:
  
    Z100324|MR|
    Z100324|MR||4|
    Z100324|MR:prd-23396378|  14674^62993,43222[EDT^prd-23396378^prd-|TCP|5001|23396378^CM66129^1
    Z100324|MR:prd-31785654|   2987^62993,44544[EDT^prd-31785654^prd-|TCP|5001|31785654^CM58902^2
    Z100324|MR:prd-33358400| 115075^62993,44166[EDT^prd-33358400^prd-|TCP|5001|33358400^CM58961^1
    Z100324|MR:prd-50135128|  14350^62993,44658[EDT^prd-50135128^prd-|TCP|5001|50135128^CM64868^1

2nd log, 5 minutes later:
  
    Z100324|MR|
    Z100324|MR||4|
    Z100324|MR:prd-23396378|  14674^62993,43222[EDT^prd-23396378^prd-|TCP|5001|23396378^CM66129^1
    Z100324|MR:prd-31785654|   2987^62993,44544[EDT^prd-31785654^prd-|TCP|5001|31785654^CM58902^2
    Z100324|MR:prd-50135128|  14350^62993,44658[EDT^prd-50135128^prd-|TCP|5001|50135128^CM64868^1

comments:
  
  - LWS CM66129 keeps the lock on #4 (Meds) is still held, so we must bump the time up
  - LWS CM58961 dropped the lock on MR:prd-33358400

### line types we might encounter:

    (a) Z12345|MR|
      features: len(split) = 3
      previous line: doesn't matter
      action: clear activities list
      
    (b) Z12345|MR||4|
      features: len(split) = 5
      previous line: could only be (a)
      action: add 4th element (activity id) to activities list

    (c) Z12345|MR:prd-55555|  14674^62993,43222[EDT^prd-55555^prd-|TCP|5001|55555^CM66129^1
      features: len(split) = 6
      previous line: decides action taken
      action:
        check if this data was in the last log file, 
        then either increase the time on the existing record if yes
        or add a new record if no
        * compare carefully if previous line was (b) (i.e. we have activities defined)

### [split](http://docs.python.org/2/library/stdtypes.html#str.split) of line type (c):

    line = Z18690|MR:prd-64815294| 900472^62993,44840[EDT^prd-64815294^prd-|TCP|5001|64815294^MSO3259^1

    line.split('|')
      00 = Z18690             -> patient_record = str.strip('Z')
      01 = MR:prd-64815294    -> app = split(':')[0]
        split(':')
          00 = MR             -> app
          01 = prd-64815294   -> (ignore, is either empty or redundant)
      02 = 900472^62993,44840[EDT^prd-64815294^prd-
        split('^,[-', 6)
          00 = 900472         -> user_id
          01 = 62993          -> (ignore, same in every line)
          02 = 44840          -> seconds_since_midnight
          03 = EDT            -> (ignore)
          04 = prd            -> (ignore)
          05 = 64815294       -> (ignore, since this process_id is redundant?)
          06 = prd-           -> (ignore)
      03 = TCP                -> (ignore)
      04 = 5001               -> (ignore)
      05 = 64815294^MSO3259^1
        split('^')
          00 = 64815294       -> process_id
          01 = MSO3259        -> workstation
          02 = 1              -> (ignore)


DATA STRUCTURES
---------------

### variables:

- loggedPrev = list of record ids that were recorded from the last log file
- loggedCur = list of record ids logged on this loop, will become loggedPrev on the next loop
- splitPrev = split list from the previous line
- splitCur = split of current line

### dframe: ([pandas.DataFrame](http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe))

- (index) = unique incrementing integer id/index
- patient_record = patient record in lock contention
- user_id = using holding the record open
- process_id = Hyperspace process number for blocking user
- workstation = where Hyperspace process is coming from
- app = Epic app (marginally useful)
- activity = activity/workflow being blocked
- first_seen = timestamp of the first file with this lock
- last_seen = timestamp of the last file with this lock (may be same as first_seen)
- total_minutes = time in minutes (convenience entry)
- seconds_since_midnight = useful for easy grouping by shifts? (only stored with first_seen time)

### activities:
(see `activities.csv`, first line is labels)

- id = integer; the activity id mentioned in line type (b)
- label = string; name of locked activity, short enough to use as chart keys
- per-encounter = boolean; if true this lock only effects one encounter, otherwise it locks for all
- comments = string; misc details

### experimenting with auto-increment id
[reference](http://stackoverflow.com/questions/14778042/)

    labels = ['pt_rec', 'proc_id', 'app']

    row1 = { 'pt_rec': 'Z00001', 'proc_id':1, 'app':'MR' }
    row2 = { 'pt_rec': 'Z00002', 'proc_id':2, 'app':'MR' }

    df = pd.DataFrame([row1, row2])

    row3 = pd.Series(['Z00003', 3, 'ADT'], labels)
    df.append(row3, ignore_index=True)

    list4 = ['Z00004', 4, 'MR']
    df.append(list4, labels)                                        --> FAIL!

    df4 = pd.DataFrame(['Z00004', 4, 'MR'], index=labels
    df.append(df4, ignore_index=True)                               --> FAIL!

    s4 = pd.Series({ 'pt_rec': 'Z00004', 'proc_id':4, 'app':'MR' }))

    labels = ['pt_rec', 'proc_id", 'app']

    row1 = { 'pt_rec': 'Z00001', 'proc_id':1, 'app':'MR' }
    row2 = { 'pt_rec': 'Z00002', 'proc_id':2, 'app':'MR' }

    df = pd.DataFrame([row1, row2])

    row3 = pd.Series(['Z00003', 3, 'ADT'], labels)
    df = df.append(row3, ignore_index=True)							            --> GOOD

    list4 = ['Z00004', 4, 'MR']
    df.append(list4, labels)										                    --> FAIL!

    df4 = pd.DataFrame(['Z00004', 4, 'MR'], index=labels)
    df.append(df4, ignore_index=True)								                --> FAIL!
    * df4 looks like rows & columns are swapped, transpose first
    df.append(df4.T, ignore_index=True)								              --> FAIL!

    s4 = pd.Series({ 'pt_rec': 'Z00004', 'proc_id':4, 'app':'MR' })	--> GOOD!
    df = df.append(s4, ignore_index=True)

    last_index = len(df)-1
    last_row = df.iloc[-1]

##### conclusion:

- build temporary record as a pd.Series, then append to the big DataFrame with `ignore_index=True`
- after appending a single row, the index is `len(dframe)-1`
- to get a row by index, use `df.iloc[#]`

### create empty DataFrame to start with
see [here](http://technicaltidbit.blogspot.com/2013/06/create-empty-dataframe-in-pandas.html) and [here](http://docs.scipy.org/doc/numpy/reference/arrays.dtypes.html)

    index_labels = ['pt_record', 'proc_id', 'user_id', 'workstation', 'app', 'activity', 'first_seen', 'last_seen', 'total_min', 'sec_since_midnight']


PSEUDOCODE
----------

### importing the logs:

    function: carryover(dframe, loggedPrev)
      foreach prevDframe in loggedPrev
        if prevDframe matches *all* of the following, return prevDframe.id:
          - dframe.patient_record
          - dframe.process_id
          - dframe.workstation
          - dframe.app
          - dframe.activity
        else return Nothing

    get log file names
    sort file names oldest-to-newest
    loop over file names
      open log file
      get timestamp from log file name
      line = readline
      splitCur = line.split('|')

      if len(splitCur)==3:
        splitPrev, activities = splitCur, []
        continue

      if len(splitCur)==5 & splitCur[3]!="":
        activities.append(splitCur[3])
        continue

      if len(splitCur)==6:
        create series from splitCur

        if carryover(dframe, series) returns id:
          dframe(id).last_seen = timestamp
          dframe(id).total_time += 5
          loggedCur.append(id)

        else: #not a carryover
          foreach activity in activities:
            series[activity] = activity #lookup activity name or stick with id?
            series[first_seen] = timestamp
            series[last_seen] = timestamp
            series[total_time] = 5
            append series to dframe
            last_index = len(dframe)-1
            loggedCur.append(last_index)

      next line
      close log file
      loggedPrev = loggedCur
      loggedCur = empty
