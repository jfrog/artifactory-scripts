#!/bin/bash

# Example script which adds configuration of a repository for locally
# generated rpms to a docker image being created.
# Because this script is called . script-name.sh it will inherit the
# global variable from the calling script.

mkdir -p work/etc/yum.repos.d

curl $artifactoryRoot/rpm-local/develop.repo -o work/etc/yum.repos.d/develop.repo
sed -i '/enabled/ d;$ ienabled=0' work/etc/yum.repos.d/develop.repo
curl $artifactoryRoot/rpm-local/release.repo -o work/etc/yum.repos.d/release.repo
sed -i '/enabled/ d;$ ienabled=1' work/etc/yum.repos.d/release.repo

cat >>work/Dockerfile <<EOF
COPY etc /etc
EOF
