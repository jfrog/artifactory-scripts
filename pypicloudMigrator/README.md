Pypicloud Migration Tool
========================

This is a simple Groovy script designed to migrate all packages from a Pypicloud
instance to an Artifactory repository. Although it was written specifically with
Pypicloud in mind, it should work equally well with any Pypi repository service.

This script requires Groovy in order to run.

Usage
-----

To run:

``` shell
./pypicloudMigrator.groovy -t 20 https://pypicloudserver/simple/ pypiuser:mypassword https://artifactoryserver/artifactory/pypi-repository/ artuser:mypassword
```

The script takes the following parameters:

1. `-t <num>`: The number of system threads to use during migration. Optional,
   default is 10.
2. The URL of the Pypicloud index. Generally this ends with `/simple/`.
   Required.
3. Credentials for the Pypicloud server, in the form `<username>:<password>`.
   Optional: if credentials are not needed to fetch packages, this can be
   omitted.
4. The URL of the Artifactory Pypi repository to which packages should be
   migrated. This is the 'standard' repository URL, e.g. use
   `artifactory/pypi-local/`, rather than `artifactory/api/pypi/pypi-local/` or
   `artifactory/api/pypi/pypi-local/simple/`. Required.
5. Credentials for the Artifactory server, in the form `<username>:<password>`.
   This user must have write permissions to the specified Pypi repository.
   Required.

After the migration completes, Artifactory might take a few minutes to index the
new packages, after which they should be usable. The script can be run against a
non-empty Artifactory repository, and will only add packages, and leave the
existing packages alone. The tool will also avoid re-uploading packages that
already exist in Artifactory.

Packages are uploaded in the Pypi 'simple' layout: each directory in the
repository root is a module name, and contains a flat set of package files for
that module. e.g. `pypi-repo/moduleName/file.whl`, not
`pypi-repo/moduleName/version/file.whl`.

Testing
-------

A test folder is included, which will run a small set of functional tests to
ensure that packages migrated by the tool can be properly installed. This
requires:

- Groovy
- Docker
- Bash
- Python 3, including pip and virtualenv
- An Artifactory license should be added as `test/artifactory.lic`

To run the tests, simply run:

``` shell
./test/PypicloudMigratorTest.groovy
```
