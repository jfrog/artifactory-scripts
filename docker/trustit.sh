#!/bin/bash

# Trustit - Sets up trust for a random docker repostory.
# usage: trustit.sh <fqdn:port> of repo you want to trust
# example: trustit.sh localhost:5001

sudo mkdir -p /etc/docker/certs.d/$1
openssl s_client -connect $1 -showcerts|openssl x509 -outform PEM|sudo tee /etc/docker/certs.d/$1/ca.crt

