The replicationDiff.sh script can be used to find the missing artifacts on your target Artifactory repository if you notice discrepancy in the artifact count after a successful replication event.





In the current working directory you will find a text file named "filepaths_uri.txt" which contains all the artifacts including metadata files that are present in the source repository and missing in the target repository. It will include the entire URL of the source Artifactory and the path to the artifact.

You will also find another text file named "filepaths_nometadatafiles.txt" which contains only the artifacts and not metadata files  that are present in the source repository and missing in the target repository. Since metadata files are not necessary as the target repository is responsible for calculating metadata, we have filtered them to only provide the missing artifacts.
