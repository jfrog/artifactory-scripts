Minimal Apache HTTPD SSL Configuration
==================================

This is a minimal SSL configuration for apache httpd.  You can use artifactory.conf as a starting point for your
installation.

To run the demo:

docker build --rm --tag art_apache_https .
docker run -d --name art_apache_https art_apache_https

#To find the IP of the newly running container use:
docker inspect --format '{{ .NetworkSettings.IPAddress }}' art_apache_https
