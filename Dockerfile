FROM python:3.8
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y memcached
RUN adduser --disabled-password --gecos "" worker
RUN mkdir -p /code/shared && chown -R worker:worker /code
COPY --chown=worker:worker . /code/
WORKDIR /code/
RUN pip install -r /code/requirements.txt
USER worker