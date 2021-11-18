FROM amazon/aws-lambda-python:3.7

ARG FUNCTION_DIR="/var/task/"


# Setup Python environment
RUN  yum install -y git && pip install poetry

COPY pyproject.toml .
COPY poetry.lock .

RUN POETRY_VIRTUALENVS_CREATE=false poetry install --no-root

COPY ./ ${FUNCTION_DIR}

# Grab the zappa handler.py and put it in the working directory
RUN ZAPPA_HANDLER_PATH=$( \
    python -c "from zappa import handler; print (handler.__file__)" \
    ) \
    && echo $ZAPPA_HANDLER_PATH \
    && cp $ZAPPA_HANDLER_PATH ${FUNCTION_DIR}


CMD [ "handler.lambda_handler" ]