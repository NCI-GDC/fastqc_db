FROM ubuntu:xenial-20161010

MAINTAINER Jeremiah H. Savage <jeremiahsavage@gmail.com>

RUN echo 'Acquire::http::Proxy "http://cloud-proxy:3128";' >> /etc/apt/apt.conf.d/01proxy \
    && echo 'Acquire::https::Proxy "http://cloud-proxy:3128";' >> /etc/apt/apt.conf.d/01proxy \
    && apt-get update \
    && apt-get install -y \
       python3-pandas \
       python3-pip \
       python3-sqlalchemy \
       unzip \
    && apt-get clean \
    && export http_proxy=http://cloud-proxy:3128 \
    && export https_proxy=http://cloud-proxy:3128 \
    && pip3 install fastqc_db \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && rm -f /etc/apt/apt.conf.d/01proxy