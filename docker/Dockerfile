FROM quay.io/jeremiahsavage/cdis_base

ENV fastqc_sqlite 0.7

RUN /bin/bash -c "source ${HOME}/.virtualenvs/p3/bin/activate \
    && pip install fastqc_sqlite"
