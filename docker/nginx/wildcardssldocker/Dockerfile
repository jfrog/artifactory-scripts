FROM jfrog/artifactory-pro
MAINTAINER Jay Denebeim <jayd@jfrog.com>

COPY local.sh /tmp
RUN bash /tmp/local.sh && rm /tmp/local.sh
RUN (cd /etc/yum.repos.d; echo -e "[nginx]\nname=nginx repo\nbaseurl=http://nginx.org/packages/centos/\$releasever/\$basearch/\ngpgcheck=0\nenabled=1" >/etc/yum.repos.d/nginx.repo)

RUN yum install nginx openssl -y

COPY artifactory.conf /etc/nginx/conf.d/

RUN yum clean all

COPY run.sh /run.sh
COPY artifactory.config.xml /etc/opt/jfrog/artifactory/artifactory.config.xml

COPY wildcard-ssl.sh /wildcard-ssl.sh
RUN bash /wildcard-ssl.sh localhost
RUN mv /certs /etc/nginx/ssl/

CMD /run.sh
