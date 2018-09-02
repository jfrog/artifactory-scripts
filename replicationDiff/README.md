The replicationDiff.sh script can be used to find the missing artifacts on your target Artifactory repository if you notice discrepancy in the artifact count after a successful replication event.

The script can be run by providing parameters or you can just run the script wihtout parameters and it will prompt you for all the details necessary to run the diff between your source Artifactory repository and target Artifactory repository.

Running the script by providing parameters:

The script needs nine parameters in order to run it. Below are these parameters

-source_adminuser (admin user)
-target_adminuser (admin user)
-source_art (your source Artifactory instance URL)
-target_art (your target Artifactory instance URL)
-source_repo (the source repository name)
-target_repo (the target repository name)
-source_password (admin user password for source Artifactory)
-target_password (admin user password for target Artifactory)
-download_missingfiles (yes or no)

Here is an example on how to run the script by providing the above parameters as flags:

./testreplication_diff.sh -source_adminuser adminuser -target_adminuser adminuser -source_art https://sourceartifactory.server.net/artifactory -target_art https://targetartifactory.server.net/artifactory -source_repo mysourcerepo-local -target_repo mytargetrepo-local -source_password password -target_password password -download_missingfiles yes or no

The -download_missingfiles flag can take yes or no as a value

If you don't want to provide parameters for the script, then you could just run the script without any of the above options and it will prompt you for all the details of the source Artifactory instance and target Artifactory instance.

After a successful run of the script it will provide you with the count of files sorted according to the file extension that are present in the source repository and are missing in the target repository. 

In the current working directory you will find a text file named "filepaths_uri.txt" which contains all the artifacts including metadata files that are present in the source repository and missing in the target repository. It will include the entire URL of the source Artifactory and the path to the artifact.

You will also find another text file named "filepaths_nometadatafiles.txt" which contains only the artifacts and not metadata files  that are present in the source repository and missing in the target repository. Since metadata files are not necessary as the target repository is responsible for calculating metadata, we have filtered them to only provide the missing artifacts.
