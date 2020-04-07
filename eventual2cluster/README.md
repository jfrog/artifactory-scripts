# eventual2cluster
This shell script should be used when migrating from an [Eventual](https://www.jfrog.com/confluence/display/RTF/Configuring+the+Filestore#ConfiguringtheFilestore-EventualBinaryProvider) to [Eventual-Cluster](https://www.jfrog.com/confluence/display/RTF/Configuring+the+Filestore#ConfiguringtheFilestore-Eventual-ClusterBinaryProvider) [filestore configuration](https://www.jfrog.com/confluence/display/RTF/Configuring+the+Filestore).

The complete migration procedure is available at: [How to migrate from "s3" to "cluster-s3"?](https://jfrog.com/knowledge-base/how-to-migrate-from-s3-to-cluster-s3/) Knowledge Base article.
This script is only a "helper" to fully complete the migration.

Instructions:
The script has to run from the $EVENTUAL_DIR/\_add/ or $EVENTUAL_DIR/\_delete/ folder.
Run the script only if there are remaining binaries in the folder.

During the script you will need to set several parameters:
1. Function - add / delete. Select according to the corresponding directory the script is running from.
2. Artifactory user - The user that runs the Artifactory process and owns the $ARTIFACTORY_HOME directory.
3. Artifactory group - The group that is associated with the $ARTIFACTORY_HOME directory.
4. Destination - The location of the "\_queue" folder. Should be $ARTIFACTORY_HOME/data/eventual/.
5. Operation - copy / move. Based on the selection the script will perform a `cp` or `mv` function. Copying is usually a safer option, but moving will be much faster and will not result in additional storage.
