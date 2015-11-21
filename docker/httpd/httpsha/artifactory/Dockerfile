FROM jfrog/artifactory-pro
MAINTAINER jayd@jfrog.com

RUN yum install uuid nfs-utils rpcbind -y
RUN yum clean all

COPY run.sh /run.sh

# set up mysql in artifactory
RUN curl http://artifactory/artifactory/jcenter/mysql/mysql-connector-java/5.1.27/mysql-connector-java-5.1.27.jar -O
RUN mv -f mysql-connector* ~artifactory/tomcat/lib
RUN cp ~artifactory/misc/db/mysql.properties ~artifactory/etc/storage.properties
RUN sed -i 's/localhost/mysql/' ~artifactory/etc/storage.properties

EXPOSE 8081 10042

CMD /run.sh
