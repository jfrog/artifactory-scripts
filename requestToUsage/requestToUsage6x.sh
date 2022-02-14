#!/bin/bash
FILE=$1
if [ ! -f $FILE ]; then
    echo "Correct usage is: requestToUsage.sh request.log"
fi
awk 'BEGIN { FS = "|" } ; NR > 1 { if ($10 != -1) {totalSum += $10} } END { print ("Total sum: " totalSum " bytes.") }' $FILE