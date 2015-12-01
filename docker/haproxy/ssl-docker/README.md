Minimal haproxy SSL with Docker Configuration
==================================

This is a minimal SSL configuration for haproxy with docker.  It assumes artifactory and haproxy are running on the same machine.
You can use haproxy/haproxy.cfg as a starting point for your installation.

To run the demo:

docker build --rm --tag art_haproxy_https_docker .
docker run -d --name art_haproxy_https_docker art_haproxy_https_docker

#To find the IP of the newly running container use:
docker inspect --format '{{ .NetworkSettings.IPAddress }}' art_haproxy_https_docker

__Note__
This assumes a file named local.sh that contains something like:

<pre>
sed -i '/mirrorlist/d;s/#baseurl/baseurl/;s~mirror.centos.org~artifactory-us.jfrog.info/artifactory~' /etc/yum.repos.d/CentOS-*.repo
rm /etc/yum.repos.d/Artifactory*
</pre>

This edits the CentOS yum repositories to point at your local artifactory.  Change the artifactory-us.jfrog.info to your
local artifactory instance.

We supply a blank one here so the Dockerfile works.

