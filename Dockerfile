# This is only intended to build the application for deployment on AWS Lambda with Zappa
# it has limited usage locally

FROM node:16-alpine AS js-static

ENV APP_DIR=/srv/app

WORKDIR $APP_DIR

COPY package.json yarn.lock $APP_DIR

RUN yarn install --frozen-lockfile

COPY assets ./assets
COPY *.config.js \
    webpack.*.js ./

RUN npm run build:prod

FROM python:3.9 AS static-files

ENV APP_DIR=/srv/app \
    POETRY_VIRTUALENVS_CREATE=false \
    # for poetry, see https://python-poetry.org/docs/master/#installing-with-the-official-installer
    PATH="/root/.local/bin:${PATH}"

WORKDIR $APP_DIR

RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.1.13 python3 -

COPY pyproject.toml poetry.lock $APP_DIR

ENV DJANGO_SETTINGS_MODULE onlineweb4.settings

RUN poetry install --no-interaction --no-ansi --no-dev

COPY . .

COPY --from=js-static $APP_DIR/webpack-stats.json ./webpack-stats.json
COPY --from=js-static $APP_DIR/bundles ./bundles

RUN ./manage.py collectstatic

FROM amazon/aws-lambda-python:3.9

LABEL maintainer="Dotkom <dotkom@online.ntnu.no>"
ENV POETRY_VIRTUALENVS_CREATE=false \
    PATH="/root/.local/bin:${PATH}"
ARG FUNCTION_DIR="/var/task/"

COPY pyproject.toml poetry.lock $FUNCTION_DIR

# Setup Python environment
RUN yum install -y git unzip \
    && curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.1.13 python3 - \
    # silent, show errors and location (aka follow redirect)
    && curl -sSL --output vault-lambda-extension.zip \
        https://releases.hashicorp.com/vault-lambda-extension/0.6.0/vault-lambda-extension_0.6.0_linux_amd64.zip \
    && unzip vault-lambda-extension.zip -d /opt \
    && poetry install --no-root --no-dev -E prod \
    && poetry cache clear . --all -n \
    && yum remove -y git unzip \
    && yum clean all \
    && rm vault-lambda-extension.zip \
    && rm -rf /var/cache/yum

COPY ./ $FUNCTION_DIR

RUN ZAPPA_HANDLER_PATH=$(python -c "from zappa import handler; print (handler.__file__)") \
    && echo $ZAPPA_HANDLER_PATH \
    && cp $ZAPPA_HANDLER_PATH $FUNCTION_DIR

COPY --from=static-files /srv/app/webpack-stats.json ./
ARG VERSION
ENV OW4_VERSION=${VERSION}
CMD [ "handler.lambda_handler" ]
