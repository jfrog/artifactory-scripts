#!/bin/bash

service haproxy start
. /etc/init.d/artifactory wait
