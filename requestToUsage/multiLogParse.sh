#!/bin/bash
LOC=$1
if [ ! -f $LOC ]; then
    echo "Correct usage is: requestToUsage.sh request.log"
fi
PREFIX=$2
for i in $LOC; do 
	./requestToUsage.sh $i $PREFIX
done