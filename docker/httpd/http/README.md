Minimal Apache HTTPD Configuration
==================================

This is a minimal configuration for apache httpd.  You can use artifactory.conf as a starting point for your
installation.

To run the demo:

docker build --rm --tag art_apache_http .
docker run -d --name art_apache_http art_apache_http

#To find the IP of the newly running container use:
docker inspect --format '{{ .NetworkSettings.IPAddress }}' art_apache_http
