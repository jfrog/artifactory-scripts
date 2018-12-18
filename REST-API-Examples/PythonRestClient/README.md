artifactopy - Artiactory's Python REST Client
=============================================

Artifactopy allows for quick use of the Artifactory REST API for the automation
of get, put, post, delete, and patch operations.

The library has been tested on and is compatible with Python 3.6 and above.

Structure
---------

The library has a structure that reflects each operation's usage and request type.
- `artifactopy.api`: (All API requests as classes)
  - `artifactopy.api.get`: (all GET requests)
  - `artifactopy.api.put`: (all PUT requests)
  - `artifactopy.api.post`: (all POST requests)
  - `artifactopy.api.patch`: (all PATCH requests)
  - `artifactopy.api.delete`: (all DELETE requests)
- `artifactopy.auth`: (Authentication classes)
- `artifactopy.models`: (JSON classes)

Examples
--------------------------------------------------------------------------------------

`test test`

*The -download_missingfiles flag can take `yes or no` as a value and when you pass `yes` the script will download all the files that are present in Source repository and missing from the Target repository to a folder 'replication_downloads' in the current working directory*

**If you don't want to provide parameters for the script, then you could just run the script without any of the above options and it will prompt you for all the details of the source Artifactory instance and target Artifactory instance.**

**NOTE:**
----------
*After a successful run of the script it will provide you with the count of files sorted according to the file extension that are present in the source repository and are missing in the target repository.*

*In the current working directory you will find a text file named **"filepaths_uri.txt"** which contains all the artifacts including metadata files that are present in the source repository and missing in the target repository. It will include the entire URL of the source Artifactory and the path to the artifact.*

*You will also find another text file named **"filepaths_nometadatafiles.txt"** which contains only the artifacts and not metadata files  that are present in the source repository and missing in the target repository. Since metadata files are not necessary as the target repository is responsible for calculating metadata, we have filtered them to only provide the missing artifacts.*
