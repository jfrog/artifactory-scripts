FROM jfrog/artifactory-pro
MAINTAINER Jay Denebeim <jayd@jfrog.com>

COPY local.sh /tmp
RUN bash /tmp/local.sh && rm /tmp/local.sh

RUN yum install httpd -y

COPY artifactory.conf /etc/httpd/conf.d/
RUN yum clean all

COPY run.sh /run.sh

CMD /run.sh
