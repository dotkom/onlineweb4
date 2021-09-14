FROM python:3.7 AS base
LABEL maintainer="Dotkom <dotkom@online.ntnu.no>"

ENV APP_DIR=/srv/app \
    POETRY_VIRTUALENVS_CREATE=false \
    TZ=Oslo/Norway

WORKDIR $APP_DIR

COPY poetry.lock pyproject.toml ./

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

RUN poetry install --no-interaction --no-ansi -E prod

ENV PYTHONUNBUFFERED 1

CMD ["bash"]

FROM base AS Full

COPY . .
