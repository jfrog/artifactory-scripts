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

Run this script only once per repository. If it is run a second time, due to the
way directory copies are handled, a second copy of the package will be inserted
inside of the original copy.
