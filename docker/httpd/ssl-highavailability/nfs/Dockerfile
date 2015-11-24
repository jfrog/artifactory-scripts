FROM debian
MAINTAINER jayd@jfrog.com

COPY local.sh /tmp
RUN bash /tmp/local.sh && rm /tmp/local.sh

RUN apt-get update || true
RUN apt-get install nfs-kernel-server dialog rsyslog inotify-tools -y
RUN apt-get clean metadata

COPY run.sh /run.sh

RUN mkdir -p /srv
RUN echo '/srv *(rw,sync,no_subtree_check,fsid=0,no_root_squash)' >>/etc/exports

EXPOSE 111 2049 1110 4045

CMD /run.sh
