FROM python:3.7-slim as builder
WORKDIR /build
COPY pyproject.toml poetry.lock ./
RUN apt-get update && apt-get install --no-install-recommends -y \
  git \
  gcc \
  && pip install --upgrade pip \
  && pip install poetry \
  && poetry export --without-hashes -E prod -f requirements.txt --output requirements.txt \
  && pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

FROM python:3.7-slim

LABEL maintainer="dotkom@online.ntnu.no"

ENV DJANGO_SETTINGS_MODULE=onlineweb4.settings POETRY_VIRTUALENVS_CREATE=false HOME=/home/onlineweb4 APP_HOME=/home/onlineweb4/onlineweb4

WORKDIR $HOME

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /build/requirements.txt .

RUN addgroup --system onlineweb4 && adduser --system --group onlineweb4 \
  && chown -R onlineweb4:onlineweb4 $HOME \
  && apt-get update && apt-get install --no-install-recommends -y mime-support \
  && pip install --upgrade pip \
  && pip install --no-cache /wheels/*

COPY . $APP_HOME
RUN chown -R onlineweb4:onlineweb4 $APP_HOME

WORKDIR $APP_HOME
EXPOSE 8000
USER onlineweb4
CMD = ["gunicorn", "onlineweb4.wsgi"]