ARG REGISTRY=docker.osdc.io/ncigdc
ARG BASE_CONTAINER_VERSION=latest

FROM ${REGISTRY}/python3.9-builder:${BASE_CONTAINER_VERSION} as builder

COPY ./ /fastqc_db

WORKDIR /fastqc_db

RUN pip install tox && tox -e build

FROM ${REGISTRY}/python3.9:${BASE_CONTAINER_VERSION}

LABEL org.opencontainers.image.title="fastqc_db" \
      org.opencontainers.image.description="fastqc_sqlite" \
      org.opencontainers.image.source="https://github.com/NCI-GDC/fastqc_db" \
      org.opencontainers.image.vendor="NCI GDC"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /fastqc_db/dist/*.whl /fastqc_db/
COPY requirements.txt /fastqc_db/

WORKDIR /fastqc_db

RUN pip install --no-deps -r requirements.txt \
	&& pip install --no-deps *.whl \
	&& rm -f *.whl requirements.txt

USER app

ENTRYPOINT ["fastqc_db"]

CMD ["--help"]
