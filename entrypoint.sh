#!/bin/bash

python manage.py migrate --noinput
uwsgi --ini uwsgi.ini --wsgi-file ./onlineweb4/wsgi.py --socket 0.0.0.0:8000
