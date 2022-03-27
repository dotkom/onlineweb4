FROM node:16-alpine as node
LABEL maintainer="Dotkom <dotkom@online.ntnu.no>"

ENV APP_DIR=/srv/app

WORKDIR $APP_DIR

COPY package.json yarn.lock $APP_DIR

RUN yarn install --frozen-lockfile

COPY . .

RUN npm run build:prod
# this builds in parallell!
FROM python:3.9
ENV APP_DIR=/srv/app POETRY_VIRTUALENVS_CREATE=false

WORKDIR $APP_DIR

RUN pip install poetry

COPY pyproject.toml poetry.lock $APP_DIR

ENV DJANGO_SETTINGS_MODULE onlineweb4.settings

RUN poetry install --no-interaction --no-ansi

COPY . .

COPY --from=node $APP_DIR/webpack-stats.json ./webpack-stats.json
COPY --from=node $APP_DIR/bundles ./bundles
RUN ./manage.py collectstatic
