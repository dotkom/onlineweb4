import os
from base import PROJECT_ROOT_DIRECTORY

DEBUG = True
TEMPLATE_DEBUG = DEBUG

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

# Email settings
# If you are actually sending mail, this should be replaced with an
# email adress you can get all mail to.
DEVELOPMENT_EMAIL = 'your_preferred_adress_here'

# Overwriting all the emails from base.py with the development email, so that
# all mail gets sent to the developer(s) instead of their actual targets.
# These variables should be used throughout the project instead of the actual
# adresses, so we can safely redirect all mail away from the live systems when
# running tests.
DEFAULT_FROM_EMAIL = 'development@online.ntnu.no'
EMAIL_ARRKOM = DEVELOPMENT_EMAIL
EMAIL_BEDKOM = DEVELOPMENT_EMAIL
EMAIL_DOTKOM = DEVELOPMENT_EMAIL
EMAIL_FAGKOM = DEVELOPMENT_EMAIL
EMAIL_PROKOM = DEVELOPMENT_EMAIL
EMAIL_TRIKOM = DEVELOPMENT_EMAIL

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # real
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # prints

# GOOGLE_ANALYTICS_KEY = 'UA-XXXX-Y'

#MEDIA_ROOT = '/var/websites/prod/onlineweb_uploads'
MEDIA_ROOT = os.path.join(PROJECT_ROOT_DIRECTORY, "uploaded_media/")

#MEDIA_URL = '//media.online.ntnu.no/'
MEDIA_URL = '/media/'

#MEDIA_ROOT = '/var/websites/prod/static'
STATIC_ROOT = os.path.join(PROJECT_ROOT_DIRECTORY, 'collected_static')
#STATIC_URL = '//static.online.ntnu.no'
STATIC_URL = '/static/'

#Url of default profile picture
DEFAULT_PROFILE_PICTURE_URL = os.path.join(STATIC_URL, "img", "profile_default.png")

# Filebrowser local settings.
FILEBROWSER_MEDIA_ROOT = MEDIA_ROOT

# If you use django extensions that should not be used in production
# add them here.
# INSTALLED_APPS += (
#   'apps.example',
#   'debug_toolbar', # https://github.com/dcramer/django-debug-toolbar
#   'django_extensions', # http://packages.python.org/django-extensions/
# )
