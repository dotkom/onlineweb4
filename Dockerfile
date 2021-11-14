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
FROM python:3.10.0-slim as builder
WORKDIR /build
COPY pyproject.toml poetry.lock ./
RUN apt-get update && apt-get install --no-install-recommends -y \
  git \
  gcc \
  python3-dev \
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
FROM nginx:alpine as onlineweb4-nginx
ENV OW4_DIR=/opt/ow4/
ENV NGINX_DJANGO_UPSTREAM=127.0.0.1:8001
ENV NGINX_PORT=8000
ENV NGINX_SERVER_NAME=localhost
COPY --from=builder /app/static ${OW4_DIR}/static

EXPOSE 8000

# ----------- ONLINEWEB4 SERVER-----------
FROM python:3.10.0-slim as onlineweb4

LABEL maintainer="dotkom@online.ntnu.no"

ENV DJANGO_SETTINGS_MODULE=onlineweb4.settings POETRY_VIRTUALENVS_CREATE=false HOME=/home/onlineweb4 APP_HOME=/home/onlineweb4/onlineweb4

WORKDIR $HOME

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /build/requirements.txt .

RUN addgroup --system onlineweb4 && adduser --system --group onlineweb4 \
  && chown -R onlineweb4:onlineweb4 $HOME \
  && apt-get update && apt-get install --no-install-recommends -y mime-support locales \
  && pip install --upgrade pip \
  && pip install --no-cache /wheels/*

WORKDIR $APP_HOME
COPY . .
COPY --from=node-builder /build/webpack-stats.json .
RUN chown -R onlineweb4:onlineweb4 .
EXPOSE 8001
USER onlineweb4

ENTRYPOINT ["uwsgi", "--socket", "127.0.0.1:8001", "--master", "--enable-threads", "--wsgi-file", "onlineweb4/wsgi.py"]
