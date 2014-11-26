#!/bin/bash

# Example script which adds configuration for epel
# Because this script is called . script-name.sh it will inherit the
# global variable from the calling script.

mkdir -p work/tmp
cat >work/tmp/fetchepel.sh <<-EOF1
        #!/bin/bash

        distro=\$(sed -n 's/^distroverpkg=//p' /etc/yum.conf)
        releasever=\$(rpm -q --qf "%{version}" -f /etc/\$distro)
        basearch=\$(rpm -q --qf "%{arch}" -f /etc/\$distro)

        cat >/etc/yum.repos.d/tmp.repo <<-EOF
[tmp]
name=epel temp repo
baseurl=$fedoraUrl/epel/\$releasever/\$basearch
gpgcheck=0
EOF
        yum --disablerepo=* --enablerepo=tmp install -y epel-release
        yum --disablerepo=* --enablerepo=tmp clean all

        rm /etc/yum.repos.d/tmp.repo
EOF1
chmod +x work/tmp/fetchepel.sh

cat >>work/Dockerfile <<EOF
COPY tmp /tmp
RUN /tmp/fetchepel.sh
RUN sed -i "\
    /baseurl/ s%http.://download.fedoraproject.org/pub/fedora%$fedoraUrl%; \
    s%file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL%$fedoraUrl/epel/RPM-GPG-KEY-EPEL%; \
    " /etc/yum.repos.d/*.repo

EOF
