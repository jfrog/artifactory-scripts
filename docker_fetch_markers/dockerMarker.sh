#!/bin/bash
echo "Enter your source Artifactory URL: "
read Source_ART_URL
SOURCE_ART=${Source_ART_URL%/}
echo "Enter your source repository name: "
read Source_repo_name
echo "Enter your docker image name: "
read docker_imagename
echo "Enter docker tag: "
read docker_tag
echo "Enter admin username for source Artifactory: "
read source_username
echo "Password for source Artifactory: "
read -s source_password

echo $SOURCE_ART
status_code=$(curl -u$source_username:$source_password --write-out %{http_code} --silent --output /dev/null "$SOURCE_ART/api/docker/$Source_repo_name/v2/$docker_imagename/manifests/$docker_tag" -L)

if [[ "$status_code" -eq 401 ]] && [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the provided admin username and password for the Source Artifactory"
  echo
  exit 0
fi

if [[ "$status_code" -eq 000 ]] && [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with Could not resolve host: $SOURCE_ART. Please check the Source Artifactory URL and make sure its correct"
  echo
  exit 0
fi

if [[ "$status_code" -eq 404 ]] && [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the Source Artifactory URL and Source Repository name provided make sure its correct. "
  echo
  exit 0
fi

if [[ "$status_code" -eq 400 ]] && [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the Source Artifactory URL and Source Repository name provided make sure its correct. "
  echo
  exit 0
fi

if [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the Source Artifactory URL and Source Repository name provided make sure its correct."
  echo
  exit 0
fi

curl -X GET -u$source_username:$source_password "$SOURCE_ART/api/docker/$Source_repo_name/v2/$docker_imagename/manifests/$docker_tag" -L > source.log

sed -n '/blobSum/p' source.log | sed 's/[",]//g' | sed 's/blobSum ://g' | sed -e 's/^[ \t]*//' > docker_uri.txt

prefix=$SOURCE_ART/api/docker/$Source_repo_name/v2/$docker_imagename/blobs/
awk -v prefix="$prefix" '{print prefix $0}' docker_uri.txt > filepaths_uri.txt

echo
echo
echo
#rm source.log
echo
echo
echo "Do you want to download all the files that are present in Source repository and missing from the Target repository?(yes/no)"
read input
if [[ $input =~ [yY](es)* ]]
then
echo "Downloading the missing files to a folder '"replication_downloads"' in the current working directory"
fi
if [[ $input =~ [nN](o)* ]]
then
echo "done"
exit 0
fi
cat filepaths_uri.txt | xargs -n 1 curl -sS -L -u$source_username:$source_password > /dev/null
