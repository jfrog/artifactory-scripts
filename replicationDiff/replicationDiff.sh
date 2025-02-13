#!/bin/bash

if [[ $# -lt 18 ]] && [[ $# -ne 0 ]]
then
echo
echo "You have not passed all the required 9 parameters or one of the parameter is missing a value"
echo "Please make sure that all of these parameters have a value -source_adminuser  -target_adminuser  -source_art  -target_art  -source_repo  -target_repo  -source_password  -target_password  -download_missingfiles"
echo
exit 0
fi

if [[ $# -gt 18 ]]
then
echo
echo "You have not passed all the required 9 parameters or one of the parameter is missing a value"
echo "Please make sure that all of these parameters have a value -source_adminuser  -target_adminuser  -source_art  -target_art  -source_repo  -target_repo  -source_password  -target_password  -download_missingfiles"
echo
exit 0
fi

if [[ $# -ne 0 ]]  
then    
while test $# -gt 0; do
           case "$1" in
                -source_adminuser)
                    shift
                    SOURCEUSER=$1
                    shift
                    ;;
                -target_adminuser)
                    shift
                    TARGETUSER=$1
                    shift
                    ;;
                     -source_art)
                    shift
                    SOURCEART=$1
                    shift
                    ;;
                     -target_art)
                    shift
                    TARGETART=$1
                    shift
                    ;;
                     -source_repo)
                    shift
                    SOURCEREPO=$1
                    shift
                    ;;
                     -target_repo)
                    shift
                    TARGETREPO=$1
                    shift
                    ;;
                     -source_password)
                    shift
                    SOURCEPASSWORD=$1
                    shift
                    ;;
                    -target_password)
                    shift
                    TARGETPASSWORD=$1
                    shift
                    ;;
                    -download_missingfiles)
                    shift
                    DOWNLOADFILES=$1
                    shift
                    ;;

                *)
                  echo 
                  echo "$1 is not a recognized flag!"
                  exit 0 
                  # return 1;
                   ;;
          esac
          done


#  echo "SOURCE_USER : $SOURCEUSER";
#  echo "TARGET_USER : $TARGETUSER";
 
 SOURCEART=${SOURCEART%/}
 TARGETART=${TARGETART%/}


status_code=$(curl -u$SOURCEUSER:$SOURCEPASSWORD --write-out %{http_code} --silent --output /dev/null "$SOURCEART/api/storage/$SOURCEREPO/?list&deep=1&listFolders=0&mdTimestamps=1&statsTimestamps=1&includeRootPath=1" -L)

if [[ "$status_code" -eq 401 ]] && [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the provided username (-source_adminuser) and password (-source_password) for the Source Artifactory" 
  echo
  exit 0
fi

if [[ "$status_code" -eq 000 ]] && [[ "$status_code" -ne 200 ]] 
  then
  echo
  echo "Request failed with Could not resolve host: $SOURCEART Please check the Source Artifactory URL (-source_art) and make sure its correct"
  echo
  exit 0
fi

if [[ "$status_code" -eq 404 ]] && [[ "$status_code" -ne 200 ]] 
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the Source Artifactory URL (-source_art) and Source Repository (-source_repo) make sure its correct. "
  echo
  exit 0
fi

if [[ "$status_code" -eq 400 ]] && [[ "$status_code" -ne 200 ]] 
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the Source Artifactory URL (-source_art) and Source Repository (-source_repo) make sure its correct. "
  echo
  exit 0
fi

if [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the Source Artifactory URL (-source_art) and Source Repository (-source_repo) make sure its correct."
  echo
  exit 0
fi

status_code=$(curl -u$TARGETUSER:$TARGETPASSWORD --write-out %{http_code} --silent --output /dev/null "$TARGETART/api/storage/$TARGETREPO/?list&deep=1&listFolders=0&mdTimestamps=1&statsTimestamps=1&includeRootPath=1" -L)

if [[ "$status_code" -eq 401 ]] && [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the provided username (-target_adminuser) and password (-target_password) for the Target Artifactory"
  echo
  exit 0
fi

if [[ "$status_code" -eq 000 ]] && [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with Could not resolve host: $TARGETART Please check the Target Artifactory URL (-target_art) and make sure its correct"
  echo
  exit 0
fi

if [[ "$status_code" -eq 404 ]] && [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the Target Artifactory URL (-target_art) and Target Repository (-target_repo) make sure its correct. "
  echo
  exit 0
fi

if [[ "$status_code" -eq 400 ]] && [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the Target Artifactory URL (-target_art) and Target Repository (-target_repo) make sure its correct. "
  echo
  exit 0
fi

if [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the Target Artifactory URL (-target_art) and Target Repository (-target_repo) make sure its correct."
  echo
  exit 0
fi

curl -X GET -u$SOURCEUSER:$SOURCEPASSWORD "$SOURCEART/api/storage/$SOURCEREPO/?list&deep=1&listFolders=0&mdTimestamps=1&statsTimestamps=1&includeRootPath=1" -L > source.log
curl -X GET -u$TARGETUSER:$TARGETPASSWORD "$TARGETART/api/storage/$TARGETREPO/?list&deep=1&listFolders=0&mdTimestamps=1&statsTimestamps=1&includeRootPath=1" -L > target.log

grep -Fxv -f target.log source.log > diff_output.txt
sed -n '/uri/p' diff_output.txt | sed 's/[<>,]//g' | sed '/https/d' | sed '/http/d' | sed  's/ //g' | sed 's/[",]//g' | sed 's/uri://g' > cleanpaths.txt
prefix=$SOURCEART/$SOURCEREPO
awk -v prefix="$prefix" '{print prefix $0}' cleanpaths.txt > filepaths_uri.txt

echo
echo
echo "Here is the count of files sorted according to the file extension that are present in the source repository and are missing in the target repository. Please note that if there are SHA files in these repositories which will have no extension, then the entire URL will be seen in the output. The SHA files will be seen for docker repositories whose layers are named as per their SHA value. "
echo
grep -E ".*\.[a-zA-Z0-9]*$" filepaths_uri.txt | sed -e 's/.*\(\.[a-zA-Z0-9]*\)$/\1/' filepaths_uri.txt | sort | uniq -c | sort -n
sed '/maven-metadata.xml/d' filepaths_uri.txt |  sed '/Packages.bz2/d' | sed '/.*gemspec.rz$/d' |  sed '/Packages.gz/d' | sed '/Release/d' | sed '/.*json$/d' | sed '/Packages/d' | sed '/by-hash/d' | sed '/filelists.xml.gz/d' | sed '/other.xml.gz/d' | sed '/primary.xml.gz/d' | sed '/repomd.xml/d' | sed '/repomd.xml.asc/d' | sed '/repomd.xml.key/d' > filepaths_nometadatafiles.txt
rm source.log target.log diff_output.txt cleanpaths.txt
echo

if [[ $DOWNLOADFILES =~ [yY](es)* ]]
then
mkdir replication_downloads
cd replication_downloads
cat ../filepaths_nometadatafiles.txt | xargs -n 1 curl -sS -L -O -u$SOURCEUSER:$SOURCEPASSWORD
echo "Downloading all the files that are present in Source repository and missing from the Target repository to a folder '"replication_downloads"' in the current working directory"
fi
if [[ $DOWNLOADFILES =~ [nN](o)* ]]
then
exit 0
fi
exit 0
fi

if [[ $# -eq 0 ]]
then
echo "Enter your source Artifactory URL: "
read Source_ART_URL
SOURCE_ART=${Source_ART_URL%/}
echo "Enter your target Artifactory URL: "
read Target_ART_URL
TARGET_ART=${Target_ART_URL%/}
echo "Enter your source repository name: "
read Source_repo_name
echo "Enter your target repository name: "
read Target_repo_name
echo "Enter admin username for source Artifactory: "
read source_username
echo "Password for source Artifactory: "
read -s source_password
echo "Enter admin username for target Artifactory: "
read target_username
echo "Password for target Artifactory: "
read -s target_password

status_code=$(curl -u$source_username:$source_password --write-out %{http_code} --silent --output /dev/null "$SOURCE_ART/api/storage/$Source_repo_name/?list&deep=1&listFolders=0&mdTimestamps=1&statsTimestamps=1&includeRootPath=1" -L)

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

status_code=$(curl -u$target_username:$target_password --write-out %{http_code} --silent --output /dev/null "$TARGET_ART/api/storage/$Target_repo_name/?list&deep=1&listFolders=0&mdTimestamps=1&statsTimestamps=1&includeRootPath=1" -L)

if [[ "$status_code" -eq 401 ]] && [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the provided admin username and password for the Target Artifactory"
  echo
  exit 0
fi

if [[ "$status_code" -eq 000 ]] && [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with Could not resolve host: $TARGET_ART Please check the Target Artifactory URL and make sure its correct"
  echo
  exit 0
fi

if [[ "$status_code" -eq 404 ]] && [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the Target Artifactory URL and Target Repository name provided make sure its correct. "
  echo
  exit 0
fi

if [[ "$status_code" -eq 400 ]] && [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the Target Artifactory URL and Target Repository name provided make sure its correct. "
  echo
  exit 0
fi

if [[ "$status_code" -ne 200 ]]
  then
  echo
  echo "Request failed with HTTP $status_code. Please check the Target Artifactory URL and Target Repository name provided make sure its correct. "
  echo
  exit 0
fi

curl -X GET -u$source_username:$source_password "$SOURCE_ART/api/storage/$Source_repo_name/?list&deep=1&listFolders=0&mdTimestamps=1&statsTimestamps=1&includeRootPath=1" -L > source.log
curl -X GET -u$target_username:$target_password "$TARGET_ART/api/storage/$Target_repo_name/?list&deep=1&listFolders=0&mdTimestamps=1&statsTimestamps=1&includeRootPath=1" -L > target.log
grep -Fxv -f target.log source.log > diff_output.txt
sed -n '/uri/p' diff_output.txt | sed 's/[<>,]//g' | sed '/https/d' | sed '/http/d' | sed  's/ //g' | sed 's/[",]//g' | sed 's/uri://g' > cleanpaths.txt
prefix=$SOURCE_ART/$Source_repo_name
awk -v prefix="$prefix" '{print prefix $0}' cleanpaths.txt > filepaths_uri.txt

echo
echo
echo "Here is the count of files sorted according to the file extension that are present in the source repository and are missing in the target repository. Please note that if there are SHA files in these repositories which will have no extension, then the entire URL will be seen in the output. The SHA files will be seen for docker repositories whose layers are named as per their SHA value. In the case of Debian repositories you will see SHA files and also metadata files with entire URL in the output as they have no extension. "
echo
grep -E ".*\.[a-zA-Z0-9]*$" filepaths_uri.txt | sed -e 's/.*\(\.[a-zA-Z0-9]*\)$/\1/' filepaths_uri.txt | sort | uniq -c | sort -n
sed '/maven-metadata.xml/d' filepaths_uri.txt |  sed '/Packages.bz2/d' | sed '/.*gemspec.rz$/d' |  sed '/Packages.gz/d' | sed '/Release/d' | sed '/.*json$/d' | sed '/Packages/d' | sed '/by-hash/d' | sed '/filelists.xml.gz/d' | sed '/other.xml.gz/d' | sed '/primary.xml.gz/d' | sed '/repomd.xml/d' | sed '/repomd.xml.asc/d' | sed '/repomd.xml.key/d' > filepaths_nometadatafiles.txt
rm source.log target.log diff_output.txt cleanpaths.txt
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
mkdir replication_downloads
cd replication_downloads
cat ../filepaths_nometadatafiles.txt | xargs -n 1 curl -sS -L -O -u$source_username:$source_password
fi