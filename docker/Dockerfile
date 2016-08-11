FROM ubuntu:xenial-20160809

MAINTAINER Jeremiah H. Savage <jeremiahsavage@gmail.com>

USER root

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-pandas \
    python3-sqlalchemy

RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV fastqc_db 0.25

RUN pip3 install fastqc_db"
