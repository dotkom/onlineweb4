FROM node:lts as webpack
LABEL maintainer="Dotkom <dotkom@online.ntnu.no>"

WORKDIR /srv/app/webpack

COPY assets assets
COPY webpack.server.js .
COPY webpack.production.config.js .
COPY webpack.config.js .
COPY package.json .
COPY .babelrc .
COPY postcss.config.js .

RUN yarn --non-interactive --no-progress --pure-lockfile && \
    yarn build:prod


FROM python:3.8-slim-buster
LABEL maintainer="dotkom@online.ntnu.no"
ENV DJANGO_SETTINGS_MODULE=onlineweb4.settings POETRY_VIRTUALENVS_CREATE=false

WORKDIR /srv/app

RUN apt-get update && apt-get install --no-install-recommends -y \
  git \
  gcc \
  curl \
  mime-support \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN pip install poetry

RUN poetry install --no-interaction --no-ansi --no-dev -E prod -E docs

COPY --from=webpack /srv/app/webpack/bundles bundles
COPY --from=webpack /srv/app/webpack/webpack-stats.json webpack-stats.json
COPY . .

RUN python manage.py collectstatic --noinput && \
    chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh" ]
