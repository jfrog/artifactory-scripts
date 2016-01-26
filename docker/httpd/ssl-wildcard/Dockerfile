FROM jfrog/artifactory-pro
MAINTAINER Jay Denebeim <jayd@jfrog.com>

COPY local.sh /tmp
RUN bash /tmp/local.sh && rm /tmp/local.sh

RUN yum install httpd mod_ssl -y

COPY artifactory.conf /etc/httpd/conf.d/

RUN yum clean all

COPY run.sh /run.sh
COPY artifactory.config.xml /etc/opt/jfrog/artifactory/artifactory.config.xml

COPY wildcard-ssl.sh /wildcard-ssl.sh
RUN bash /wildcard-ssl.sh localhost
RUN mv /certs/*.crt /etc/pki/tls/certs/
RUN mv /certs/*.key /etc/pki/tls/private/

CMD /run.sh
