FROM python:3.7-slim as base
RUN groupadd -r pubsub -g 1000 &&\
    useradd --no-log-init -r -g pubsub -u 1000 pubsub &&\
    mkdir -p /project/run &&\
    chown -R pubsub:pubsub /project/run
WORKDIR /project/run
RUN pip install "python-dateutil>=2.7.2,<2.8"
RUN pip install "asyncio-nats-client>=0.8.2,<0.9"
RUN pip install "nats-python>=0.4.0,<0.5"
COPY --chown=pubsub:pubsub ./pubsub /project/run/pubsub
USER pubsub

FROM base as http
USER root
RUN pip install "flask>=1.0.2,<1.1"
COPY --chown=pubsub:pubsub ./api /project/run/api
USER pubsub
ENV FLASK_APP=api/web.py
CMD flask run --host 0.0.0.0

FROM base as dev
USER root
RUN mkdir -p /home/pubsub &&\
    chown -R pubsub:pubsub /home/pubsub
RUN pip install "ipython>=7.4.0,<7.5"
USER pubsub
CMD ipython
