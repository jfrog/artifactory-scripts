#!/usr/bin/env bash

/etc/init.d/nginx start &
. /etc/init.d/artifactory wait
