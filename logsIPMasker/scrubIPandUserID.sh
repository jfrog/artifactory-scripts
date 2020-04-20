#!/bin/sh
CURRENT_DIR=$pwd
echo $currentDir
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

echo "Looking for UserID and IP to replace in request, audit, and access files..."
find $BUNDLE_DIR -type f \( -name 'access*.log' -o -name 'audit*.log' -o -name 'request*.log' -o -name 'artifactory*.log' \) | while read line; do
if [[ ${line##*/} == "access"*".log" ]]
    then
      echo "found access file, $line scrubbing sensitive data inside"
      sed -i.jfrogbkp 's/client :.*/client : Scrubbed the IP and User/' $line
    elif [[ ${line##*/} == "audit"*".log" ]]
    then
      echo "found audit file, $line scrubbing sensitive data inside"
      sed -i.jfrogbkp "s|Token.*|Scrubbed Line Due To Security|" $line 
    elif [[ ${line##*/} == "artifactory"*".log" ]]
    then
      echo "found artifactory file, $line scrubbing sensitive data inside"
      sed -i.jfrogbkp -e 's/\( *user:  *\)[^ ]*\(.*\)*$/ User: ScrubbedUserID\2/Ig' -e ':a' -e 's/\( *user:  *\)[^ ]*\(.*\)*$/ User: ScrubbedUserID\2/' -e 'ta' $line
      sed -i.jfrogbkp -e 's/\( *user *\)[^ ]*\(.*\)*$/User: ScrubbedUserID\2/Ig' -e ':a' -e 's/\( *user *\)[^ ]*\(.*\)*$/ User: ScrubbedUserID\2/' -e 'ta' $line
      sed -i.jfrogbkp -e 's/\( *username  *\)[^ ]*\(.*\)*$/ User: ScrubbedUserID\2/Ig' -e ':a' -e 's/\( *username  *\)[^ ]*\(.*\)*$/ User: ScrubbedUserID\2/' -e 'ta' $line
      sed -i.jfrogbkp -e 's/\( *user named  *\)[^ ]*\(.*\)*$/ User: ScrubbedUserID\2/Ig'  $line
      sed -i.jfrogbkp -e 's/\( *User not found:  *\)[^ ]*\(.*\)*$/ Could not find User: ScrubbedUserID\2/Ig' $line
      sed -i.jfrogbkp -e 's/\( *authentication failed for *\)[^ ]*\(.*\)*$/ authentication failed for User: ScrubbedUserID\2/Ig' $line
      sed -i.jfrogbkp -e 's/\( *token for subject *\)[^ ]*\(.*\)*$/ token for User: ScrubbedUserID\2/Ig' $line
      sed -i.jfrogbkp -e 's/\( *Auto-Creation of *\)[^ ]*\(.*\)*$/ Auto-Creation of User: ScrubbedUserID\2/Ig' $line
    elif [[ ${line##*/} == "request"*"log" ]]
    then
      echo "found request file, $line scrubbing sensitive data inside"
      awk -F"|" -v OFS="|" '$3 { $4="ScubbedIP"} 1' $line | awk -F"|" -v OFS="|" '$3 { $5="ScrubbedUser"} 1' > ${line}.tmp && mv ${line}.tmp ${line}  
    fi
 
done

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
mv JFrogBundleCleanIPs* $CURRENT_DIR
echo "DONE"

