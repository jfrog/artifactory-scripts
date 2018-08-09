#!/bin/bash
FILE=$1
if [ ! -f $FILE ]; then
    echo "Correct usage is: requestToUsage.sh request.log [optional prefix string for output file]"
fi
PREFIX=$2

calculate_gigabytes () {
  # from https://unix.stackexchange.com/a/374877
  echo "$1" | awk '{ split( "B KB MB GB TB PB" , v ); s=1; while( $1>1024 ){ $1/=1024; s++ } printf "%.2f %s", $1, v[s] }'
}

# Gets first 8 characters of first timestamp ie YYYYMMDD
OUTPUT=${PREFIX:+${PREFIX}-}$(head -c 8 $FILE).csv

# Replaces | with ,
# Skips any 0-byte requests
# gsub should exist in most implementations of awk
awk '{ gsub(/[|]/, ",") }; !/,0$/' $FILE > $OUTPUT

echo "Successfully reformatted $FILE to CSV"

echo "Successfully reformatted $FILE to CSV as $OUTPUT"

# Reads output and assigns into an array for easier indexing below
DATES_IN_FILE=($(awk -F',' '{print $1}' $OUTPUT | cut -c1-8 | uniq))

for eachday in "${DATES_IN_FILE[@]}"; do
  DAY_TOTAL=0
  for requestsize in $(awk -v day="^$eachday" -F',' '{ if ( $0 ~ day){ print $NF }}' $OUTPUT); do
    let "DAY_TOTAL += requestsize";
  done
  echo "$eachday had $(calculate_gigabytes $DAY_TOTAL) transferred"
done
TOTAL=0
for request in $(awk -F',' '{ print $NF }' $OUTPUT ); do
  let "TOTAL += request";
done
FILE_TOTAL=$(calculate_gigabytes $TOTAL)

echo "Approximate data transfer total between ${DATES_IN_FILE[0]} and ${DATES_IN_FILE[@]: -1} is $FILE_TOTAL"

echo "0,0,0,0,0,0,0,0,0,0,=SUM(J:J)/(1024^3)" >> $OUTPUT
echo "Added calculation line."
echo "Open $OUTPUT in excel or a similar spreadsheet program"
