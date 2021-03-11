#!/bin/bash
FILE=$1
if [ ! -f $FILE ]; then
    echo "Correct usage is: requestToUsage.sh request.log [optional prefix string]"
fi
PREFIX=$2

OUTPUT=${PREFIX:+${PREFIX}-}$(head -c 8 $FILE).csv

awk '!/0$/' $FILE > $OUTPUT
if sed --version 
then sed "s/[|]/,/g" $OUTPUT -i
else
	echo "Please ignore the above error message from sed, switching to gsed."
	gsed "s/[|]/,/g" $OUTPUT -i
fi
echo "Successfully outputted to $OUTPUT"
if date --version
then echo 'date'
else 
	echo "Please ignore the above error message from date, switching to gdate."
	echo 'gdate'
fi

echo "0,0,0,0,0,0,0,0,=SUM(I:I)/(1024^3),0,0" >> $OUTPUT
echo "Added calculation line."
echo "Open $OUTPUT in excel or a similar spreadsheet program"
