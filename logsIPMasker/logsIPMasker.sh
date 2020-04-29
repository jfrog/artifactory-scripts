#!/bin/bash

read -p "Please enter the \$BUNDLE_DIR. This will be a directory where the files to mask are located. `echo $'\n> '`" BUNDLE_DIR
echo "Provided BUNDLE_DIR is: $BUNDLE_DIR, continue?"
select yin in "yes" "no"; do
    case $yin in
        yes ) echo "Continuing"; break;;
        no  ) echo "Exiting"; exit;;
    esac
done


echo "Searching for archives to extract..."
while [ "`find $BUNDLE_DIR -type f \( -name '*.zip' -o -name '*.tgz' -o -name '*.gz' -o -name '*.tar.gz' \) | wc -l`" -gt 0 ]
do
  find $BUNDLE_DIR -type f \( -name '*.zip' -o -name '*.tgz' -o -name '*.gz' -o -name '*.tar.gz' \) | while read line; do
    echo "Found archive: $line"
    cd $(dirname $line)
    echo "Current pwd: $(pwd)"
    echo "Unarchiving..."
    if [ ${line: -4} == ".zip" ]
    then
      echo "This is a zip file. Using unzip."
      unzip $line
    elif [ ${line: -3} == ".gz" ]
    then
      echo "This is a gz file. Using gunzip."
      gunzip $line
    else
      echo "This is a tar archive. Using tar."
      tar zxvf $line
    fi
    echo "Extraction finished. Deleting file."
    rm $line
    echo "Deleted successfully."
  done
done
echo "No archives remaining."

echo "Looking for strings to replace in all files..."
find $BUNDLE_DIR -type f -name "*" | while read line; do
  echo "Replacing IPs in file: $line "
  sed -i.jfrogbkp 's/\([0-9]\{2,3\}\.\)\{3,3\}[0-9]\{1,3\}/x.x.x.x/g' $line
done

echo "Starting cleaning all tmp files"
find $BUNDLE_DIR -type f -name "*.jfrogbkp" -delete
echo "Finished cleaning all tmp files"

echo "Starting to zip all"
cd $BUNDLE_DIR
rm .\!*\!*.*
zip -r JFrogBundleCleanIPs.$(date +%Y%m%d%H%M%S).zip .
echo "DONE"
