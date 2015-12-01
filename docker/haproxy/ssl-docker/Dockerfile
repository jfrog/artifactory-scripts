FROM jfrog/artifactory-pro
MAINTAINER Jay Denebeim <jayd@jfrog.com>

COPY local.sh /tmp
RUN bash /tmp/local.sh && rm /tmp/local.sh

RUN yum install haproxy -y

COPY haproxy /etc/haproxy/

RUN yum clean all

COPY artifactory.config.xml /etc/opt/jfrog/artifactory/artifactory.config.xml

RUN openssl req -nodes -x509 -newkey rsa:4096 -keyout localhost.key -out localhost.pem -days 356 \
    -subj "/C=US/ST=California/L=SantaClara/O=IT/CN=localhost"

RUN mkdir /etc/haproxy/ssl
RUN cat localhost.pem localhost.key >/etc/haproxy/ssl/localhost.pem

COPY server.xml /opt/jfrog/artifactory/tomcat/conf/server.xml

COPY run.sh /run.sh
CMD /run.sh
