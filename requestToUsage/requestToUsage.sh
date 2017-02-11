#!/bin/bash
FILE=$1
if [ ! -f $FILE ]; then
    echo "Correct usage is: requestToUsage.sh request.log"
fi
awk '!/0$/' $FILE > request.csv
if sed --version 
then sed "s/[|]/,/g" request.csv -i
else 
	echo "Please ignore the above error message from sed, switching to gsed."
	gsed "s/[|]/,/g" request.csv -i
fi
echo "Successfully outputted to request.csv"
echo "0,0,0,0,0,0,0,0,0,0,=SUM(J:J)/(1024^3)" >> request.csv
echo "Added calculation line."
echo "Open request.csv in excel or a similar spreadsheet program"
