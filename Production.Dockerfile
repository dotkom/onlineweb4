FROM python:3.7-slim-buster
LABEL maintainer="dotkom@online.ntnu.no"
ENV DJANGO_SETTINGS_MODULE=onlineweb4.settings POETRY_VIRTUALENVS_CREATE=false

WORKDIR /srv/app
COPY pyproject.toml poetry.lock ./

RUN apt-get update && apt-get install --no-install-recommends -y \
  git \
  gcc \
  curl \
  mime-support \
  && rm -rf /var/lib/apt/lists/* \
  && pip install poetry \
  && poetry install --no-interaction --no-ansi --no-dev -E prod


COPY log/.gitkeep log/.gitkeep
COPY middleware middleware
COPY scripts scripts
COPY utils utils
COPY templates templates
COPY onlineweb4 onlineweb4
COPY apps apps
COPY manage.py manage.py
COPY webpack-stats.json webpack-stats.json

EXPOSE 8000

ENTRYPOINT ["gunicorn", "onlineweb4.wsgi"]
