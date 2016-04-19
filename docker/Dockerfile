FROM quay.io/jeremiahsavage/cdis_base

ENV fastqc_sqlite 0.8

RUN /bin/bash -c "source ${HOME}/.virtualenvs/p3/bin/activate \
    && pip install fastqc_sqlite"
