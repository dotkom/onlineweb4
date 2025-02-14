# This is only intended to build the application for deployment on AWS Lambda with Zappa
# it has limited usage locally

FROM node:20-alpine AS js-static

ARG ENVIRONMENT
ENV ENVIRONMENT=$ENVIRONMENT
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

COPY --from=ghcr.io/astral-sh/uv:0.6.0 /uv /bin/uv

COPY pyproject.toml uv.lock $APP_DIR

ENV DJANGO_SETTINGS_MODULE=onlineweb4.settings

COPY . .

COPY --from=js-static $APP_DIR/webpack-stats.json ./webpack-stats.json
COPY --from=js-static $APP_DIR/bundles ./bundles

RUN uv run --locked -- ./manage.py collectstatic

FROM python:3.12 AS vault-lambda-extension

WORKDIR /vault

# https://developer.hashicorp.com/vault/docs/platform/aws/lambda-extension
ADD --checksum=sha256:69b95ca2f99196868077fa5d360db24aaed16fdf6038e72273163aa4cc372b0b \ 
    https://releases.hashicorp.com/vault-lambda-extension/0.10.3/vault-lambda-extension_0.10.3_linux_amd64.zip \
    /vault.zip

RUN python -m zipfile -e /vault.zip /vault

FROM amazon/aws-lambda-python:3.12

COPY --from=ghcr.io/astral-sh/uv:0.6.0 /uv /bin/uv

ARG FUNCTION_DIR="/var/task/"

COPY pyproject.toml uv.lock $FUNCTION_DIR

# offline to skip uv isntalling dependencies before the export
RUN uv export --format requirements-txt --extra prod --locked --no-cache --offline | uv pip install -r=- --verify-hashes --no-cache --system --compile-bytecode && rm /bin/uv

COPY ./ $FUNCTION_DIR

RUN ZAPPA_HANDLER_PATH=$(python -c "from zappa import handler; print (handler.__file__)") \
&& echo $ZAPPA_HANDLER_PATH \
&& cp $ZAPPA_HANDLER_PATH $FUNCTION_DIR

COPY --from=static-files /srv/app/webpack-stats.json ./
COPY --from=vault-lambda-extension /vault/extensions/vault-lambda-extension /opt/extensions/vault-lambda-extension
RUN chmod +x /opt/extensions/vault-lambda-extension
ARG VERSION
# https://docs.sentry.io/platforms/python/guides/logging/configuration/releases/#setting-a-release
ENV SENTRY_VERSION=${VERSION}
CMD [ "handler.lambda_handler" ]
