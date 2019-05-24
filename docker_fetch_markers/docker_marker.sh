#!/bin/bash
echo "Enter your Artifactory URL: "
read Source_ART_URL
SOURCE_ART=${Source_ART_URL%/}
echo "Enter your docker remote repository name without the '-cache' suffix: "
read Source_repo_name
echo "Enter admin username for Artifactory: "
read source_username
echo "Password for Artifactory: "
read -s source_password

echo
REMOTE_REPO=${Source_repo_name}-cache
#echo $REMOTE_REPO
echo

curl -X POST -u$source_username:$source_password $SOURCE_ART/api/search/aql -d 'items.find({"$and": [{"repo" : "'"$REMOTE_REPO"'"}, {"name" : {"$match" : "*.marker"}}]})' -H "Content-Type: text/plain" > marker_layers.txt

jq -M -r '.results[] | "\(.path)/blobs/\(.name)"' marker_layers.txt > marker_paths.txt

#sed 's/[",]//g' marker_paths.txt | sed 's|library/||g' | sed 's/.marker//g' | sed "s/__/:/g" | sed 's|/.*blobs|/blobs|' > download_markers.txt
sed 's/[“,]//g' download_markers.txt | sed 's|library/||g' | sed 's/.marker//g' | sed "s/__/:/g" | awk 'sub("[/][^,;/]+[/]blobs/", "/blobs/", $0)' > download_markers.txt

while read p; do


prefix=$SOURCE_ART/api/docker/$Source_repo_name/v2/$p
#awk -v prefix="$prefix" '{print prefix $0}' docker_uri.txt > filepaths_uri.txt

curl -u$source_username:$source_password $prefix > /dev/null
#cat filepaths_uri.txt | xargs -n 1 curl -sS -L -u$source_username:$source_password > /dev/null
#rm source.log docker_uri.txt filepaths_uri.txt
done <download_markers.txt
