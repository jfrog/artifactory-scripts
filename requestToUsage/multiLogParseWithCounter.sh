#!/bin/bash
LOC=$1
DELIMITER=$2
${LOC:-"."}
if [ ! -d $LOC ]; then
    echo "Usage is: ./multiLogParseWithCounter.sh /path/to/logs/ <DELIMITER> <OPTIONAL_PREFIX>"
else
    echo "Using directory $LOC as LOC"
fi
COUNTER=1
cd $LOC
for i in artifactory-request.*; do
  .\requestToUsage.sh $LOC\\$i $DELIMITER $COUNTER
   COUNTER=$(( COUNTER + 1 ))
done
