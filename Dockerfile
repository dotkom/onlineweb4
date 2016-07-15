FROM python:3
MAINTAINER Sklirg
EXPOSE 8001

RUN mkdir -p /srv/onlineweb4
WORKDIR /srv/onlineweb4

RUN curl -sL https://deb.nodesource.com/setup_4.x | bash -
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    nodejs \
    libjpeg-dev \
    ghostscript
RUN npm install -g less

RUN mkdir -p /srv/env
COPY requirements.txt /srv/onlineweb4/requirements.txt
WORKDIR /srv/env
RUN pip install -r /srv/onlineweb4/requirements.txt

ENV DJANGO_SETTINGS_MODULE onlineweb4.settings
ENV DATABASE_URL postgres://postgres@db/postgres
# ENV PATH "docker run -it –rm -v $(pwd):$(pwd) -w $(pwd) ewoutp/lessc :$PATH"

WORKDIR /srv/onlineweb4
