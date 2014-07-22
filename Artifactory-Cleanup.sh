#!/bin/bash
#replace <username> with your artifactory username
#replace <password> with your artifactory password
#replace <domain> with your artifactory domain name
# pass to the script the $START_TIME for minimum creation time in milliseconds of artifacts  (example 1325376000000 for January 1st 2012)
# pass to the script the $END_TIME for maximum creation time in milliseconds of artifacts  (example 1388534400000 for January 1st 2014)
# pass to the script the $REPO for the repository where artifacts are located (example: releases)

# find all artifacts created in 2013, time are expressed in milliseconds
# grep look for uri attribute in JSON results returned then awk take the corresponding value of the uri attribute. The first 2 sed commands remove the last character and the last sed command remove the first character, ie stripping off the comma and double quotes from the URL in awk  
RESULTS=`curl -s -X GET -u <username>:<password> "https://<domain>.artifactoryonline.com/<domain>/api/search/creation?from=$START_TIME&to=$END_TIME&repos=$REPO" | grep uri | awk '{print $3}' | sed s'/.$//' | sed s'/.$//' | sed -r 's/^.{1}//'`
for RESULT in $RESULTS ; do
    echo "fetching path from $RESULT"
    # from the URL we fetch the download uri to remove
    # grep look for downloadUri attribute in JSON results returned then awk take the corresponding value of the downloadUri attribute. The first 2 sed commands remove the last character and the last sed command remove the first character, ie stripping off the comma and double quotes from the URL in awk
    PATH_TO_FILE=`curl -s -X GET -u <username>:<password> $RESULT | grep downloadUri | awk '{print $3}' | sed s'/.$//' | sed s'/.$//' | sed -r 's/^.{1}//'`
    echo "deleting path $PATH_TO_FILE"
    # deleting the corresponding artifact at last
    curl -X DELETE -u <username>:<password> $PATH_TO_FILE
done
