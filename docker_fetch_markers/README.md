Script to replace marker files in Artifactory docker remote repository cache with actual docker layers 
======================================================================================================

The script will prompt for the Artifactory server details when you run it.

- Artifactory URL
- Docker remote repository name in Artifactory (make sure to provide the repsoitory name without the '-cache' suffix)
- Username for Artifactory (provide a user who has 'Read' and 'Deploy' priveleges to the Docker remote repository in Artifactory)
- Password for Artifactory

Once these details have been provided the script will find all the marker layers in the given docker remote repository and prompt the user for an input(yes/no) for downloading the actual layers. If the user enters 'no', then the download of the layers will be skipped, which is like a dry run option. If the user enters 'yes', then the download of the actual layers starts and you will see the progress bar for each layer with the below status details.

- HTTP status code
- Time taken in seconds for download of the layer
- Size of the layer downloaded in bytes
