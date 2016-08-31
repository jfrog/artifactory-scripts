# PyQt4 box for artifactory-scripts/4.x-migration/packageType.py

FROM debian:latest
MAINTAINER <Michael Rollins/mrollins@lifesize.com>

# Update apt sources
RUN echo 'deb http://ftp.utexas.edu/debian/ jessie main contrib' |tee -a /etc/apt/sources.list
RUN echo 'deb-src http://ftp.utexas.edu/debian/ jessie main contrib' |tee -a /etc/apt/sources.list

# Install Qt4
RUN apt-get update && \
    apt-get install -y \
	git \
	wget \
	curl \
	vim \
	python-qt4 \
	pyqt4-dev-tools

# Clean packages
RUN apt-get clean

# you must edit this to match your own user
ENV HOSTUID 1000
RUN useradd --uid $HOSTUID -m -s /bin/bash qt4
RUN usermod -a -G video,audio,tty qt4
USER qt4
WORKDIR /home/qt4
ENV QT_GRAPHICSSYSTEM=native

# Get artifactory-scripts
RUN git clone https://github.com/JFrogDev/artifactory-scripts.git

CMD ["/home/qt4/artifactory-scripts/4.x-migration/packageType.py"] 

# docker run --rm -it --net host -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix qt4dock:dev
