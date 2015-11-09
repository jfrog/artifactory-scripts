#!/usr/bin/env bash

/etc/init.d/httpd start &
/etc/init.d/artifactory wait
