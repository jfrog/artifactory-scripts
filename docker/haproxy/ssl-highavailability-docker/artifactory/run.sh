#!/bin/bash

ha_home=/srv/artifactory

service rpcbind start
mount nfs:/srv /srv

node=$(echo $MYSQL_NAME |sed 's~^.*_\([0-9]\)/.*~\1~') c
cp /license/artifactory-H${node}.lic /etc/opt/jfrog/artifactory/artifactory.lic

if [[ "$node" == "1" ]]; then
    if [ ! -d $ha_home/ha-etc ]; then
        mkdir -p $ha_home/{ha-etc/{UI,plugins},ha-data/{filestore,tmp},ha-backup}
        echo security.token=$(uuid) >$ha_home/ha-etc/cluster.properties
    
        cp /etc/opt/jfrog/artifactory/storage.properties $ha_home/ha-etc/
        chown -R artifactory: $ha_home
    fi
    if [ ! -e $ha_home/ha-etc/artifactory.config.latest.xml ]; then
        mv -f ~artifactory/etc/artifactory.config.xml $ha_home/ha-etc/
    fi
else
    while [ ! -e $ha_home/ha-etc/cluster.properties ]; do
        sleep 10
    done
fi

cat >/etc/opt/jfrog/artifactory/ha-node.properties <<EOF
node.id="artifactory-${node}"
cluster.home=$ha_home
primary=$( [[ "$node" == "1" ]] && echo true || echo false)
context.url=http://$(hostname -I|awk '{print $1}'):8081/artifactory
membership.port=10042
EOF

. /etc/init.d/artifactory wait

umount /srv
