#!/bin/bash
FILE=$1
if [ ! -f $FILE ]; then
    echo "Correct usage is: requestToUsage.sh request.log"
fi
awk 'BEGIN { FS = "|" } ; NR > 1 { downloadSum += $9; if ($8 != -1) {uploadSum +=$8} } END { print ("Download sum: "  downloadSum  ", Upload sum: "  uploadSum  " bytes.") }' $FILE
