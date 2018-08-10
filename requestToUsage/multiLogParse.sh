#!/bin/bash
LOC=$1
: ${LOC:-"."}
if [ ! -d $LOC ]; then
    echo "Usage is: ./multiLogParse.sh /path/to/logs/ [optional prefix string for output files]"
else
    echo "Using directory $LOC as LOC"
fi
PREFIX=$2
for i in $LOC/request.*; do
	./requestToUsage.sh $i $PREFIX
done
