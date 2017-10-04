Artifactory Drop Bad Properties Script
======================================

The Artifactory UI enforces certain validation rules on property keys, to keep
them from containing special characters or being special values. However, the
REST API does not enforce these rules prior to Artifactory 5.5.2, due to a
[bug][]. This can cause problems when replicating or exporting repositories.

[bug]: https://www.jfrog.com/jira/browse/RTFACT-14030

This script will delete all properties with invalid keys from your Artifactory
instance.

Usage
-----

Download `dropBadProperties.groovy`, and run it:

``` shell
groovy dropBadProperties.groovy http://localhost:8088/artifactory/ admin:password
```

Use your own Artifactory url and a privileged username and password/API key.
This script requires [Groovy](http://groovy-lang.org/) to run.

The script will log each property it deletes to both the console and to a
`dropBadProperties.log` file in the working directory (if this file already
exists, it will be appended to). Finally, the script will log the number of
properties it has deleted in total. Any errors will also be logged, but the
script will continue running if possible.
