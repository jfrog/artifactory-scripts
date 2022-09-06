#!/bin/bash
FILE=$1
if [ ! -f $FILE ]; then
    echo "Correct usage is: requestToUsage.sh request.log [optional delimiter] [optional prefix string]"
fi
DELIMITER=$2

if [ -z "$2" ]
  then
    echo "No argument supplied for delimiter. Set comma as delimiter"
    DELIMITER=','
fi
PREFIX=$3

OUTPUT=${PREFIX:+${PREFIX}-}$(head -c 10 $FILE)_POST_Requests_Only.csv

awk '/POST/' $FILE > $OUTPUT
if sed --version
then sed "s/[$DELIMITER]/,/g" $OUTPUT -i
echo "I am in sed with out error"
else
	echo "Please ignore the above error message from sed, switching to gsed."
	gsed "s/[$DELIMITER]/,/g" $OUTPUT -i
fi
echo "Successfully outputted to $OUTPUT"
if date --version
then echo 'date'
else
	echo "Please ignore the above error message from date, switching to gdate."
	echo 'gdate'
fi
awk -v var=$OUTPUT -F',' '{sum+=$10;}END{print var "|" sum}' $OUTPUT >> DataUsageSummary.txt

OUTPUT=${PREFIX:+${PREFIX}-}$(head -c 10 $FILE)_GET_Requests_Only.csv

awk '/GET/' $FILE > $OUTPUT
if sed --version
then sed "s/[$DELIMITER]/,/g" $OUTPUT -i
else
	echo "Please ignore the above error message from sed, switching to gsed."
	gsed "s/[$DELIMITER]/,/g" $OUTPUT -i
fi
echo "Successfully outputted to $OUTPUT"
if date --version
then echo 'date'
else
	echo "Please ignore the above error message from date, switching to gdate."
	echo 'gdate'
fi
awk -v var=$OUTPUT -F',' '{sum+=$10;}END{print var "|" sum}' $OUTPUT >> DataUsageSummary.txt
