#!/bin/bash
#replace $ARTIFACTORY_USER with your artifactory username
#replace $ARTIFACTORY_PASSWORD with your artifactory password
#replace http://127.0.0.1:8081/ with your artifactory domain name
# pass to the script the $START_TIME for minimum creation time in milliseconds of artifacts https://currentmillis.com/ (example 1325376000000 for January 1st 2012)
# pass to the script the $END_TIME for maximum creation time in milliseconds of artifacts https://currentmillis.com/ (example 1388534400000 for January 1st 2014)
# pass to the script the $REPO for the repository where artifacts are located (example: releases)

RESULTS=`curl -u $ARTIFACTORY_USER:$ARTIFACTORY_PASSWORD "http://127.0.0.1:8081/artifactory/api/search/creation?from=$START_TIME&to=$END_TIME&repos=$REPO" | grep uri | awk '{print $3}' | sed s'/.$//' | sed s'/.$//' | sed -r 's/^.{1}//' | sed -r 's|/api/storage||'`
curl -X DELETE -u $ARTIFACTORY_USER:$ARTIFACTORY_PASSWORD $RESULTS
