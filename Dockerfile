# ------- STATIC BUILDER --------
FROM node:lts as node-builder
WORKDIR /build
COPY package.json \
  yarn.lock \
  webpack.production.config.js \
  webpack.config.js \
  .babelrc \
  ./
COPY assets assets
RUN yarn --non-interactive --no-progress --pure-lockfile && yarn build:prod

# ------- PYTHON BUILDER --------
FROM python:3.7-slim as builder
WORKDIR /build
COPY pyproject.toml poetry.lock ./
RUN apt-get update && apt-get install --no-install-recommends -y \
  git \
  gcc \
  && pip install --upgrade pip \
  && pip install poetry \
  && poetry export --without-hashes -E prod -f requirements.txt --output requirements.txt \
  && pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt \
  && pip install -r requirements.txt

WORKDIR /app
COPY . .
COPY --from=node-builder /build/bundles bundles

RUN python manage.py collectstatic --noinput

# ------- NGINX ---------
FROM nginx:alpine as static-server
ENV OW4_DIR=/opt/ow4/
COPY static-files.conf.template /etc/nginx/templates/
COPY --from=builder /app/static ${OW4_DIR}/static

# ----------- ONLINEWEB4 SERVER-----------
FROM python:3.7-slim

LABEL maintainer="dotkom@online.ntnu.no"

ENV DJANGO_SETTINGS_MODULE=onlineweb4.settings POETRY_VIRTUALENVS_CREATE=false HOME=/home/onlineweb4 APP_HOME=/home/onlineweb4/onlineweb4

WORKDIR $HOME

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /build/requirements.txt .

RUN addgroup --system onlineweb4 && adduser --system --group onlineweb4 \
  && chown -R onlineweb4:onlineweb4 $HOME \
  && apt-get update && apt-get install --no-install-recommends -y mime-support \
  && pip install --upgrade pip \
  && pip install --no-cache /wheels/*

WORKDIR $APP_HOME
COPY . .
COPY --from=static-builder /build/webpack-stats.json .

USER onlineweb4

CMD = ["gunicorn", "onlineweb4.wsgi"]

