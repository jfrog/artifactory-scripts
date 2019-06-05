import os
import subprocess


def run(cmd):
    ret = os.system(cmd)
    if ret != 0:
        raise Exception("Command failed: %s" % cmd)

# Assuming local = conan_server and Artifactory remotes
output = subprocess.check_output("conan search * --remote=local --raw")
packages = output.decode("utf-8").splitlines()

for package in packages[:1]:
    print("Downloading %s" % package)
    run("conan download {} --remote=local".format(package))

run("conan upload * --all --confirm -r=artifactory")
