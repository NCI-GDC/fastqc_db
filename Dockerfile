FROM ubuntu:xenial-20161010

MAINTAINER Jeremiah H. Savage <jeremiahsavage@gmail.com>

RUN apt-get update \
    && apt-get install -y \
       python3-pandas \
       python3-pip \
       python3-sqlalchemy \
       unzip \
    && apt-get clean \
    && pip3 install fastqc_db \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*