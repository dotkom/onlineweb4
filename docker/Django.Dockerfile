FROM python:3.9
LABEL maintainer="Dotkom <dotkom@online.ntnu.no>"

ENV APP_DIR=/srv/app/ POETRY_VIRTUALENVS_CREATE=false
ENV LC_ALL nb_NO.UTF-8
ENV LANG nb_NO.UTF-8
ENV LANGUAGE nb_NO.UTF-8

WORKDIR $APP_DIR

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    ghostscript \
    && rm -rf /var/lib/apt/lists/* \
    && pip install poetry \
    locales \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i '/nb_NO.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen

COPY poetry.lock pyproject.toml $APP_DIR

RUN poetry install --no-interaction --no-ansi

ENV DJANGO_SETTINGS_MODULE onlineweb4.settings

ENV PYTHONUNBUFFERED 1

CMD ["bash"]
