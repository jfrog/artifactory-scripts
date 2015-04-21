To Use the NPM Migrate function:
1. In the Artifactory instance to which you want to migrate the npm registry packages, please create npm remote repository pointing to the source registry.
2. Clone the artifactory-scripts/npm/npm-migrate folder
3. Inside the conf directory, edit the config.json file as follows:
    a. For the "sourceRegUrl", please configure the URL of a source npm registry (currently the default npm registry URL us configured there).  Note: please do not change anything after the registry, just the base URL
   b. For the "targetRegUrl", please configure the URL of the remote npm repo in Artifactory according ti the following pattern: http://<artifactory-host>/artifactory/api/npm/<remote repository>).
4. CD into the extracted directory (npm-migrate).
5. Run> npm install
6. Run> run.sh (or run.bat).
