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

curl -X POST -sS -u$source_username:$source_password $SOURCE_ART/api/search/aql -d 'items.find({"$and": [{"repo" : "'"$REMOTE_REPO"'"}, {"name" : {"$match" : "*.marker"}}]})' -H "Content-Type: text/plain" > marker_layers.txt

jq -M -r '.results[] | "\(.path)/blobs/\(.name)"' marker_layers.txt > marker_paths.txt

sed 's/[“,]//g' marker_paths.txt | sed 's|library/||g' | sed 's/.marker//g' | sed "s/__/:/g" | awk 'sub("[/][^,;/]+[/]blobs/", "/blobs/", $0)' > download_markers.txt

echo "Here are the number of marker layers in this repository"
echo 
cat ~/Downloads/download_markers.txt | wc -l
echo
echo "Do you want to download these marker layers?(yes/no)"
read input
if [[ $input =~ [yY](es)* ]]
then
while read p; do

prefix=$SOURCE_ART/api/docker/$Source_repo_name/v2/$p

curl -u$source_username:$source_password --progress-bar -w "HTTP/1.1 %{http_code} OK | %{time_total} seconds | %{size_download} bytes\\n" $prefix -o /dev/null
done <download_markers.txt
fi
rm marker_layers.txt marker_paths.txt download_markers.txt
if [[ $input =~ [nN](o)* ]]
then
echo "Skipping the download of marker layers"
fi
