FROM amazon/aws-lambda-python:3.9
ENV POETRY_VIRTUALENVS_CREATE=false
ARG FUNCTION_DIR="/var/task/"

COPY pyproject.toml poetry.lock $FUNCTION_DIR

# Setup Python environment
RUN yum install -y git unzip && pip --no-cache-dir install poetry \
    && curl --silent https://releases.hashicorp.com/vault-lambda-extension/0.6.0/vault-lambda-extension_0.6.0_linux_amd64.zip \
        --output vault-lambda-extension.zip \
    && unzip vault-lambda-extension.zip -d /opt \
    && yum clean all && rm -rf /var/cache/yum \
    && poetry install --no-root \
    && poetry cache clear . --all -n

COPY ./ $FUNCTION_DIR

RUN ZAPPA_HANDLER_PATH=$(python -c "from zappa import handler; print (handler.__file__)") \
    && echo $ZAPPA_HANDLER_PATH \
    && cp $ZAPPA_HANDLER_PATH $FUNCTION_DIR

# Local image
COPY --from=dotkomonline/ow4-static /srv/app/webpack-stats.json ./

CMD [ "handler.lambda_handler" ]