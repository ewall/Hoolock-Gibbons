.
zl
cycle
 n quitFlag
 f  d  q:quitFlag  ;loop on no condition, i.e. do it forever. CTRL-C to quit, but will quit if there was an error creating the file
 . d lockInfo  ;do the lockInfo sub
 . h 300  ;change this to change logging interval
 q
lockInfo n file,err,eptID,nextNode,nextNextNode,filePath
 s filePath="/workspace/wallae/lock logging/"_$$dateString()_".txt"  ;This is where we'll save the file. The filename is the date/time of the log.
 s file=$$fopen^%ZaHMENU(filePath,"W",.err)  ;Create a file for writing here
 i err]"" s quitFlag q  ;If there was a problem, quit
 u 0  ;Write something to the screen
 w !,"Logging to ",filePath
 u file  ;Start writing stuff to the file we opened
 f  s eptID=$o(^HULOCK("EPT",eptID)) q:eptID=""  d   ;loop through the ^HULOCK global for patients
 . f  s nextNode=$o(^HULOCK("EPT",eptID,nextNode)) q:nextNode=""  d  ;loop through the locks for this patient
 . . w !,eptID,"|",nextNode,"|",^HULOCK("EPT",eptID,nextNode)  ;write out the lock info for this patient
 . . f  s nextNextNode=$o(^HULOCK("EPT",eptID,nextNode,nextNextNode)) q:nextNextNode=""  d  ;look through the extra lock info
 . . . w !,eptID,"|",nextNode,"|",^HULOCK("EPT",eptID,nextNode),"|",nextNextNode,"|",^HULOCK("EPT",eptID,nextNextNode)  ;write out the extra lock info if it exists
 u 0  ;start writing to the screen again
 s %=$$fclose^%ZaHMENU(file)  ;close the file
 q
dateString() n inst,day,mon,date,year,time,v,string
 s inst=$$dm^%Zelibb()  ;Get the current instant in human-readable format
 s day=$p(inst," ",1)  ;parse the day, month, date, year
 s mon=$p(inst," ",2)
 s date=+$p(inst," ",3)
 s year=$p(inst," ",4)
 s time=$$tout^%Zelibb($p($h,",",2),1)  ;get current military time
 s string=year_"_"_mon_"_"_date_"_("_time_")"  ;make a string of the current year_month_date_(time)
 q string
 
 
d cycle