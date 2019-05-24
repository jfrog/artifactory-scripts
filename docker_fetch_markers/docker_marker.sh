#!/bin/bash
echo "Enter your Artifactory URL: "
read Source_ART_URL
SOURCE_ART=${Source_ART_URL%/}
echo "Enter your docker remote repository name without the '-cache' suffix: "
read Source_repo_name
echo "Enter username with Read and Deploy permissions to the above repository in Artifactory: "
read source_username
echo "Password for Artifactory: "
read -s source_password

echo
REMOTE_REPO=${Source_repo_name}-cache
#echo $REMOTE_REPO

status_code=$(curl -X POST -sS -u$source_username:$source_password --write-out %{http_code} --silent --output /dev/null $SOURCE_ART/api/search/aql -d 'items.find({"$and": [{"repo" : "'"$REMOTE_REPO"'"}, {"name" : {"$match" : "*.marker"}}]})' -H "Content-Type: text/plain")

if [[ "$status_code" -eq 401 ]] && [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the provided username and password for Artifactory" 
  echo
  exit 0
fi

if [[ "$status_code" -eq 000 ]] && [[ "$status_code" -ne 200 ]] 
  then
  echo
  echo "Request failed with Could not resolve host: $SOURCEART Please check the Artifactory URL and make sure its correct"
  echo
  exit 0
fi

if [[ "$status_code" -eq 404 ]] && [[ "$status_code" -ne 200 ]] 
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the Artifactory URL and Remote Repository and make sure its correct. "
  echo
  exit 0
fi

if [[ "$status_code" -eq 400 ]] && [[ "$status_code" -ne 200 ]] 
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the Artifactory URL and Remote Repository and make sure its correct. "
  echo
  exit 0
fi

if [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the Artifactory URL and Remote Repository make and sure its correct."
  echo
  exit 0
fi

curl -X POST -sS -u$source_username:$source_password $SOURCE_ART/api/search/aql -d 'items.find({"$and": [{"repo" : "'"$REMOTE_REPO"'"}, {"name" : {"$match" : "*.marker"}}]})' -H "Content-Type: text/plain" > marker_layers.txt

jq -M -r '.results[] | "\(.path)/blobs/\(.name)"' marker_layers.txt > marker_paths.txt

sed 's/[“,]//g' marker_paths.txt | sed 's|library/||g' | sed 's/.marker//g' | sed "s/__/:/g" | awk 'sub("[/][^,;/]+[/]blobs/", "/blobs/", $0)' > download_markers.txt

echo "Here are the number of marker layers in this repository"
echo 
cat download_markers.txt | wc -l
echo
echo "Do you want to download these marker layers?(yes/no)"
read input
if [[ $input =~ [yY](es)* ]]
then
while read p; do

prefix=$SOURCE_ART/api/docker/$Source_repo_name/v2/$p

curl -sS -u$source_username:$source_password -w "HTTP/1.1 %{http_code} OK | %{time_total} seconds | %{size_download} bytes\\n" $prefix -o /dev/null &
done <download_markers.txt
fi
rm marker_layers.txt marker_paths.txt download_markers.txt
if [[ $input =~ [nN](o)* ]]
then
echo "Skipping the download of marker layers"
fi
