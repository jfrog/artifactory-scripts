HAProxy SSL High Availability Configuration
========================================================

This is a minimal high availability SSL configuration for the HAProxy.  It assumes artifactory and haproxy are running
on the same machine.
You can use artifactory.conf as a starting point for your installation.

HA artifactory cannot run in one container we need a couple of artifactories, a mysql server, and an nfs server, so 
compose is used instead of just docker build.  Unfortunately docker-compose is probably not already installed on your
system.  So, we'll include instructions for installing that as well

To run the demo either:

You _must_ have licenses for your artifactory instances available.  They need to be in a specific format, in the home
directory of the user running this configuration there needs to be a directory named license each license must be
of the format artifactory-H?.lic where ? is the node number of the artifactory you're starting.

<pre>
# install the stand alone docker compose
curl -L https://github.com/docker/compose/releases/download/1.5.1/docker-compose-`uname -s`-`uname -m`|sudo dd of=/usr/local/bin/docker-compose
sudo chmod /usr/local/bin/docker-compose
</pre>
or

<pre>
# Get the containerized docker-compose startup script
curl -L https://github.com/docker/compose/releases/download/1.5.1/run.sh | sudo tee /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
</pre>

Once docker-compose is installed you run:

`docker-compose up`

<pre>
#To find the IP of the newly running container use:
docker inspect --format '{{ .NetworkSettings.IPAddress }}' httpsha_httpd_1
</pre>

__Note__
This assumes a file named local.sh that contains something like:

<pre>
sed -i '/mirrorlist/d;s/#baseurl/baseurl/;s~mirror.centos.org~artifactory-us.jfrog.info/artifactory~' /etc/yum.repos.d/CentOS-*.repo
rm /etc/yum.repos.d/Artifactory*
</pre>

This edits the CentOS yum repositories to point at your local artifactory.  Change the artifactory-us.jfrog.info to your
local artifactory instance.

We supply a blank one here so the Dockerfile works.

