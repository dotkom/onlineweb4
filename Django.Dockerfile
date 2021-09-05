FROM python:3.8.10
LABEL maintainer="Dotkom <dotkom@online.ntnu.no>"

ENV APP_DIR=/srv/app POETRY_VIRTUALENVS_CREATE=false

RUN mkdir -p $APP_DIR

COPY poetry.lock pyproject.toml /$APP_DIR/

WORKDIR $APP_DIR

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

RUN poetry install --no-interaction --no-ansi -E prod

ENV DJANGO_SETTINGS_MODULE onlineweb4.settings

ENV PYTHONUNBUFFERED 1

CMD ["bash"]
