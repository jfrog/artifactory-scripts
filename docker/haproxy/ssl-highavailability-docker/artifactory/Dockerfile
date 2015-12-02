FROM jfrog/artifactory-pro
MAINTAINER jayd@jfrog.com

RUN yum install uuid nfs-utils rpcbind -y
RUN yum clean all

COPY run.sh /run.sh

# set up mysql in artifactory
RUN curl http://artifactory/artifactory/jcenter/mysql/mysql-connector-java/5.1.27/mysql-connector-java-5.1.27.jar -O
RUN mv -f mysql-connector* ~artifactory/tomcat/lib
COPY server.xml /opt/jfrog/artifactory/tomcat/conf/server.xml
RUN cp ~artifactory/misc/db/mysql.properties ~artifactory/etc/storage.properties
RUN sed -i 's/localhost/mysql/' ~artifactory/etc/storage.properties

COPY artifactory.config.xml /etc/opt/jfrog/artifactory/artifactory.config.xml
RUN chown -Rc artifactory: /etc/opt/jfrog/artifactory

EXPOSE 8081 10042

CMD /run.sh
