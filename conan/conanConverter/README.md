conanConverter.py
=================

This script will copy Conan packages in the layout
`[name]/[version]/[user]/[channel]` to the layout
`[user]/[name]/[version]/[channel]` in the same repository. Since this is a
copy, the original package will still exist.

To run:

```
./conanConverter.py <artifactory url> <username> <password> <source repository> <destination repository>
```
so if you followed the steps above it will look something like:

IMPORTANT:
Run this script only once per repository. If it is run a second time, due to the
way directory copies are handled, a second copy of the package will be inserted
inside of the original copy.


To use this script to migrate from a pre-5.6 artifactory to one before 5.10.1
first create two generic repos: conan-generic-copy-local and conan-generic-newlayout-local
then copy all date from your conan repository to conan-generic-copy-local
Then run the script, then copy it back.  Assuming that your starting point is conan-local,
once you create the repo it should look something like this:
(assumes you have JFrog CLI installed, as well as python2 operating on the command python2)

```
jfrog rt cp --server-id=localhost conan-local conan-generic-copy-local
./conanConverter.py http://localhost:8081/artifactory/ admin password conan-generic-copy-local conan-generic-newlayout-local
jfrog rt del --server-id=localhost conan-local
jfrog rt cp --server-id=localhost conan-generic-newlayout-local conan-local
```
Once you have verified everything is good, you can delete the two generic repositories.
