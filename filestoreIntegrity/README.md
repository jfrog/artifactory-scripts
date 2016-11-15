Artifactory Filestore Integrity Checker
=======================================

The `filestoreIntegrity.py` script can be used to check for inconsistencies in
your Artifactory filestore. This is useful, for example, when some external
process has deleted files directly from the filestore. When the tool is run, it
attempts to request every file listed on the Artifactory instance, and it logs
file paths that respond with conspicuous response codes (basically, any response
code other than 200 or 404 will trigger this). These are most likely the missing
artifacts.

This script requires [Python 3][] to run. It is recommended that you have the
latest version installed.

To run this tool, use (for example):  
`./filestoreIntegrity.py http://localhost:8080/artifactory`

This tool supports a number of command line options:
- **--help:** Display a help and usage message.
- **--user:** Specify a username (and optionally a password) to log in with.
- **--output-file:** Specify a file to write the output to. If this is omitted
  or "-", stdout is used.

[Python 3]: https://www.python.org/downloads/
