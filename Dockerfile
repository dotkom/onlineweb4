FROM python:3
MAINTAINER Sklirg
EXPOSE 8000

ENV APP_DIR=/srv/app

RUN mkdir -p $APP_DIR
WORKDIR $APP_DIR

RUN curl -sL https://deb.nodesource.com/setup_4.x | bash -
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    nodejs \
    libjpeg-dev \
    ghostscript
RUN npm install -g less

COPY requirements.txt $APP_DIR/requirements.txt
RUN pip install -r $APP_DIR/requirements.txt
COPY requirements-prod.txt $APP_DIR/requirements-prod.txt
RUN pip install -r $APP_DIR/requirements-prod.txt

ENV DJANGO_SETTINGS_MODULE onlineweb4.settings
ENV DATABASE_URL postgres://postgres@db/postgres

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
