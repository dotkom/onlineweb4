import os
from base import PROJECT_ROOT_DIRECTORY
DEBUG = True
TEMPLATE_DEBUG = DEBUG
ASSETS_DEBUG = DEBUG

DATABASES = {
    #'default': {
        #'ENGINE': 'django.db.backends.postgresql_psycopg2',
        #'NAME': 'django',
        #'USER': 'django',
        #'PASSWORD': 'django',
        #'HOST': '127.0.0.1',
        #'PORT': '',
    #},
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}


#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # real
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # prints

#MEDIA_ROOT = '/var/websites/prod/onlineweb_uploads'
MEDIA_ROOT = os.path.join(PROJECT_ROOT_DIRECTORY, "uploaded_media/")

#MEDIA_URL = '//media.online.ntnu.no/'
MEDIA_URL = '/media/'


#MEDIA_ROOT = '/var/websites/prod/static'
STATIC_ROOT = os.path.join(PROJECT_ROOT_DIRECTORY, 'collected_static')
#STATIC_URL = '//static.online.ntnu.no'
STATIC_URL = '/static/'

# If you use django extensions that should not be used in production
# add them here.
# INSTALLED_APPS += (
#   'apps.example',
#   'debug_toolbar', # https://github.com/dcramer/django-debug-toolbar
#   'django_extensions', # http://packages.python.org/django-extensions/
# )
