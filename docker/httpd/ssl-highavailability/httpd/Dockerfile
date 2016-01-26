FROM ubuntu
MAINTAINER Jay Denebeim <jayd@jfrog.com>

COPY local.sh /tmp
RUN bash /tmp/local.sh && rm /tmp/local.sh

RUN apt-get update ; apt-get install -y apache2 \
    && a2dissite 000-default \
    && a2enmod rewrite \
    && a2enmod headers \
    && a2enmod lbmethod_byrequests \
    && a2enmod proxy \
    && a2enmod proxy_balancer \
    && a2enmod proxy_http \
    && a2enmod ssl \
    || true

COPY artifactory.conf /etc/apache2/sites-available/
RUN a2ensite artifactory

COPY run.sh /run.sh

RUN mkdir -p /etc/pki/tls/certs /etc/pki/tls/private
RUN openssl req -nodes -x509 -newkey rsa:4096 -keyout /etc/pki/tls/private/example.key -out /etc/pki/tls/certs/example.pem -days 356 \
    -subj "/C=US/ST=California/L=SantaClara/O=IT/CN=localhost"

CMD /run.sh
