migrate.py
==========

The purpose of this script is to migrate all the Conan recipes and binary packages from a Conan remote to a different one.
In particular, can be used to migrate the Conan packages from a conan server to Artifactory.

The script will migrate from a remote named ``local`` to a remote named ``artifactory``. 
If your remote names are different edit the script and modify the ``-r=local`` and ``-r=artifactory``.

The script requires [Python 2 or 3](https://www.python.org/downloads/) installed and [Conan client](https://conan.io) installed.

To run this tool, use:  

```
$ python migrate.py
```
