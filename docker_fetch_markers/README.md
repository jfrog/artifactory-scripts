Script to replace marker files in Artifactory docker remote repository cache with actual docker layers 
======================================================================================================

**The script will require cURL and jq(command line json processor) installed in order to work**

The script will prompt for the Artifactory server details when you run it.

- Artifactory URL
- Docker remote repository name in Artifactory (make sure to provide the repsoitory name without the '-cache' suffix)
- Username for Artifactory (provide a user who has 'Read' and 'Deploy' priveleges to the Docker remote repository in Artifactory)
- Password for Artifactory

Once these details have been provided the script will display the number of marker layers in the given docker remote repository and prompt the user for an input(yes/no) for downloading the actual layers. If the user enters 'no', then the download of the layers will be skipped, which is like a dry run option. If the user enters 'yes', then the download of the actual layers starts and you will see the below status details for each downloaded layer.

- HTTP status code
- Time taken in seconds for download of the layer
- Size of the layer downloaded in bytes

Once all the downloads are complete you could run the script again to see if there are any marker layers left in the docker remote repository.
