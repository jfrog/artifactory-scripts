RestoreTrashcan.rb
==================

Usage
-----

1. Ensure that Ruby is installed
2. Install the `rest-client` library by running `gem install rest-client`
3. Edit `RestoreTrashcan.rb`:
   - Change the value of the `artifactory` variable to the url of your
     Artifactory server
   - Change the values of the `user_name` and `password` variables to the
     username and password of an admin user on your Artifactory server
4. Run `ruby RestoreTrashcan.rb`

This script will restore all artifacts from the trash, one artifact at a time.
If this is interrupted at any point, running the command again will start where
the process left off. The script will print one line for each artifact it has
attempted to restore, with the artifact's path and the response code from the
server. In the event of an error code, the response body will also be printed,
and the script will continue to the next artifact.
