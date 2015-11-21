sed -i '/mirrorlist/d;s/#baseurl/baseurl/;s~mirror.centos.org~artifactory-us.jfrog.info/artifactory~' /etc/yum.repos.d/*.repo 2>/dev/null
rm /etc/yum.repos.d/Artifactory* 2>/dev/null
sed -i 's%https*://[a-z.]*archive.ubuntu.com%http://artifactory-us.jfrog.info/artifactory/%;s/^deb-src/#deb-src/;/ppa/s~ppa.launchpad.net~artifactory-us.jfrog.info/artifactory/ppa~' $(find /etc/apt/sources.list* -name *list 2>/dev/null) 2>/dev/null
sed -i '/debian/{/security/d;s~/.*\.[^/]*~//artifactory-us.jfrog.info/artifactory~}' /etc/apt/sources.list /etc/apt/sources.list.d/*.list 2>/dev/null
exit 0
