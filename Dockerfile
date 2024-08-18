# This is only intended to build the application for deployment on AWS Lambda with Zappa
# it has limited usage locally

FROM node:20-alpine AS js-static

ENV APP_DIR=/srv/app
ENV NODE_ENV=production

WORKDIR $APP_DIR

COPY package.json package-lock.json $APP_DIR

RUN npm ci

COPY assets ./assets
COPY esbuild.mjs ./

RUN npm run build

FROM python:3.12 AS static-files

ENV APP_DIR=/srv/app

WORKDIR $APP_DIR

COPY --from=ghcr.io/astral-sh/uv:0.2.37 /uv /bin/uv
COPY pyproject.toml uv.lock $APP_DIR

ENV DJANGO_SETTINGS_MODULE=onlineweb4.settings

COPY . .

COPY --from=js-static $APP_DIR/webpack-stats.json ./webpack-stats.json
COPY --from=js-static $APP_DIR/bundles ./bundles

RUN uv run --locked -- ./manage.py collectstatic

FROM amazon/aws-lambda-python:3.12

COPY --from=ghcr.io/astral-sh/uv:0.2.37 /uv /bin/uv

ARG FUNCTION_DIR="/var/task/"

COPY pyproject.toml uv.lock $FUNCTION_DIR

# Setup Python environment
RUN dnf install -y unzip \
    # silent, show errors and location (aka follow redirect)
    && curl -sSL --output vault-lambda-extension.zip \
        https://releases.hashicorp.com/vault-lambda-extension/0.10.3/vault-lambda-extension_0.10.3_linux_amd64.zip \
    && unzip vault-lambda-extension.zip -d /opt \
    && dnf remove -y unzip \
    && dnf clean all \
    && rm vault-lambda-extension.zip \
    && rm -rf /var/cache/dnf

RUN uv sync --no-dev --extra prod --locked --no-cache && rm /bin/uv

ENV VIRTUAL_ENV=/var/task/.venv
ENV PATH="/var/task/.venv/bin:$PATH"

COPY ./ $FUNCTION_DIR

RUN ZAPPA_HANDLER_PATH=$(python -c "from zappa import handler; print (handler.__file__)") \
    && echo $ZAPPA_HANDLER_PATH \
    && cp $ZAPPA_HANDLER_PATH $FUNCTION_DIR

COPY --from=static-files /srv/app/webpack-stats.json ./
ARG VERSION
# https://docs.sentry.io/platforms/python/guides/logging/configuration/releases/#setting-a-release
ENV SENTRY_VERSION=${VERSION}
CMD [ "handler.lambda_handler" ]
