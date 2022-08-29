#!/bin/bash
LOC=$1
${LOC:-"."}
if [ ! -d $LOC ]; then
    echo "Usage is: ./multiLogParse.sh /path/to/logs/ <OPTIONAL_PREFIX>"
else
    echo "Using directory $LOC as LOC"
fi
COUNTER=1
cd $LOC
for i in artifactory-request.*; do
  .\requestToUsage.sh $LOC\\$i $COUNTER
   COUNTER=$(( COUNTER + 1 ))
done
