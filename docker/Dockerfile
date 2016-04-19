FROM quay.io/jeremiahsavage/cdis_base

USER root

RUN apt-get update && apt-get install -y --force-yes \
    unzip

USER ubuntu

ENV fastqc_sqlite 0.16

RUN /bin/bash -c "source ${HOME}/.virtualenvs/p3/bin/activate \
    && pip install fastqc_db"
