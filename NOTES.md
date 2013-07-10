NOTES
=====

These are my random notes as I'm working thru the data and figuring out how to process it.


TIMESTAMP
---------

### example filenames:
- `2013_Jul_1_(0001).txt`
- `2013_Jul_1_(0006).txt`

### reference:
[http://docs.python.org/2/library/time.html#time.strptime]()

### code:
    from datetime import datetime
    strptime_template = "%Y_%b_%d_(%H%M).txt"
    timestamp = datetime.strptime(filename, strptime_template)

### comments:
This filename scheme (as I've already mentioned to CK) doesn't sort right, but we can fix it in the future. I'd prefer something akin to [ISO 8601](https://xkcd.com/1179/).

Since the logs need to be processed in order, maybe it's best to just
rename all the files ahead of time, to simplify the file slurp?


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
      action: clear section list
      
    (b) Z12345|MR||4|
      features: len(split) = 5
      previous line: could only be (a)
      action: add 4th element (section id) to section list

    (c) Z12345|MR:prd-55555|  14674^62993,43222[EDT^prd-55555^prd-|TCP|5001|55555^CM66129^1
      features: len(split) = 6
      previous line: decides action taken
      action:
        check if this data was in the last log file, 
        then either increase the time on the existing record if yes
        or add a new record if no
        * compare carefully if previous line was (b) (i.e. we have sections defined)

### [split](http://docs.python.org/2/library/stdtypes.html#str.split) of line type (c):

    line = Z18690|MR:prd-64815294| 900472^62993,44840[EDT^prd-64815294^prd-|TCP|5001|64815294^MSO3259^1

    line.split('|')
      00 = Z18690             -> *needed for comparing with previous line
      01 = MR:prd-64815294    -> app = split(':')[0]
        split(':')
          00 = MR             -> app
          01 = prd-64815294   -> (ignore, is either empty or redundant)
      02 = 900472^62993,44840[EDT^prd-64815294^prd-
        split('^,[-', 6)
          00 = 900472         -> ??
          01 = 62993          -> (ignore, same in every line)
          02 = 44840          -> ??
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

### dframe ([pandas.DataFrame](http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe))

- id = unique incrementing integer id/index
- app = Epic app (marginally useful)
- process_id = Hyperspace process number for blocking user
- workstation = where Hyperspace process is coming from
- sections = multiple-item list of the locked sections (pipe-separated?)
- first_seen = timestamp of the first file with this lock
- last_seen = timestamp of the last file with this lock (may be same as first_seen)
- total_time = time in minutes (convenience entry)

##### TBD:

- mrn = record being blocked
- user = using holding the record open
- what else ??

### sections:

see `sections.csv`, first line is labels

- id = integer; the section id mentioned in line type (b)
- label = string; name of locked activity, short enough to use as chart keys
- not-per-encounter = boolean; if true this lock only effects one encounter, otherwise it locks for all
- comments = string; misc details


PSEUDOCODE
----------

### importing the logs:

    function: carryover(dframe, loggedPrev)
      foreach prevDframe in loggedPrev
        if prevDframe matches *all* of the following, return prevDframe.id:
          - dframe.app
          - dframe.process_id
          - dframe.workstation
          - dframe.sections *sorted for comparison?
        else return Nothing

    get log file names
    sort file names oldest-to-newest
    loop over file names
      open log file
      get timestamp from log file name
      line = readline
      splitCur = line.split('|')

      if len(splitCur)==3:
        splitPrev, section = splitCur, []
        continue

      if len(splitCur)==5 & splitCur[3]!="":
        section.append(splitCur[3])
        continue

      if len(splitCur)==6:
        create dframe from splitCur

        if carryover(dframe) returns id:
          dframe(id).last_seen = timestamp
          dframe(id).total_time += 5
          save dframe
          loggedCur.append(id)

        else: #not a carryover
          new_index = *how???
          dframe(new_index).first_seen = timestamp
          dframe(new_index).last_seen = timestamp
          dframe(new_index).total_time = 5
          save dframe
          loggedCur.append(new_index)

      next line
      close log file
      loggedPrev = loggedCur
      loggedCur = empty
    next log file
