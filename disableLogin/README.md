disableLogin.py
===============

The purpose of this tool is to disable internal logins for SSO users. It will
do this for all users that fit the following criteria:
- The user is not an admin.
- The user's realm is not "internal".

Note that the user's realm only describes their most recent login. If, for
example, the user normally logs in with OAuth, but their most recent login was
with their internal password, they would show up as an internal user and their
login would not be disabled by this tool. If this is a potential problem, you
can pass the `--verbose` option and grep the output for skipped users, and
manually disable internal logins for those users.

This script requires [Python 2][] to run.

To run this tool, use (for example):  
`./disableLogin.py http://localhost:8080/artifactory`

This tool supports a couple of command line options:
- **--help:** Display a help and usage message.
- **--user:** Specify a username (and optionally a password) to log in with.
- **--verbose:** Print verbose output (without this option, a successful run
  will not print anything).

[Python 2]: https://www.python.org/downloads/
