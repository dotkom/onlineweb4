# -*- coding: utf8 -*-
import os
import sys

import dj_database_url
from decouple import config
from django.contrib.messages import constants as messages

from .base import PROJECT_ROOT_DIRECTORY, PROJECT_SETTINGS_DIRECTORY

TEST_RUNNER = config("OW4_DJANGO_TEST_RUNNER", default="onlineweb4.runner.PytestTestRunner")

DEBUG = config("OW4_DJANGO_DEBUG", cast=bool, default=True)

INTERNAL_IPS = (
    '127.0.0.1',
)

ALLOWED_HOSTS = config("OW4_DJANGO_ALLOWED_HOSTS", default='*')

ADMINS = (
    ('dotKom', 'dotkom@online.ntnu.no'),
)
MANAGERS = ADMINS

DATABASES = {
    # Set this using the environment variable "DATABASE_URL"
    'default': dj_database_url.config(default="sqlite:///%s/db.db" % PROJECT_ROOT_DIRECTORY),
}

# Email settings
DEFAULT_FROM_EMAIL = 'online@online.ntnu.no'
EMAIL_ARRKOM = 'arrkom@online.ntnu.no'
EMAIL_BEDKOM = 'bedkom@online.ntnu.no'
EMAIL_DOTKOM = 'dotkom@online.ntnu.no'
EMAIL_EKSKOM = 'ekskom@online.ntnu.no'
EMAIL_FAGKOM = 'fagkom@online.ntnu.no'
EMAIL_HS = 'hs@online.ntnu.no'
EMAIL_ITEX = 'itex@online.ntnu.no'
EMAIL_OPPTAK='opptak@online.ntnu.no'
EMAIL_PROKOM = 'prokom@online.ntnu.no'
EMAIL_TRIKOM = 'trikom@online.ntnu.no'
EMAIL_XSPORT = 'x-sport@online.ntnu.no'

EMAIL_BACKEND = config("OW4_DJANGO_EMAIL_BACKEND", default='django.core.mail.backends.console.EmailBackend')

# We will receive errors and other django messages from this email
SERVER_EMAIL = 'onlineweb4-error@online.ntnu.no'

TIME_ZONE = 'Europe/Oslo'

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'nb'
LANGUAGES = (
                ('nb', 'Norwegian'),
                ('en_US', 'English'),
            )
LOCALE_PATHS = [
    os.path.join(PROJECT_ROOT_DIRECTORY, 'locale'),
]

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
DATETIME_FORMAT = 'N j, Y, H:i'
SECRET_KEY = config("OW4_DJANGO_SECRET_KEY", default='override-this-in-local.py')

# Session cookie expires after one year
SESSION_COOKIE_AGE = 31540000

# Override this to change what is the base url of the web server, e.g. localhost or staging.
BASE_URL = config("OW4_DJANGO_BASE_URL", default='https://online.ntnu.no')

AUTH_USER_MODEL = 'authentication.OnlineUser'
LOGIN_URL = '/auth/login/'

# Define where media (uploaded) files are stored
MEDIA_ROOT = config("OW4_DJANGO_MEDIA_ROOT", default=os.path.join(PROJECT_ROOT_DIRECTORY, 'uploaded_media'))
MEDIA_URL = '/media/'

# Define where static files are stored
STATIC_ROOT = config("OW4_DJANGO_STATIC_ROOT", default=os.path.join(PROJECT_ROOT_DIRECTORY, 'static'))
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT_DIRECTORY, 'files/static'),
    os.path.join(PROJECT_ROOT_DIRECTORY, 'assets'),
    os.path.join(PROJECT_ROOT_DIRECTORY, 'bundles'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Prefix for default profile picture
DEFAULT_PROFILE_PICTURE_PREFIX = os.path.join(STATIC_URL, "img", "profile_default")


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            os.path.join(PROJECT_ROOT_DIRECTORY, 'templates/')
        ],
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "sekizai.context_processors.sekizai", # Wiki

                # Onlineweb4 specific context processors
                "onlineweb4.context_processors.context_settings",
                "onlineweb4.context_processors.feedback_notifier",
            ],
            'debug': DEBUG,
        }
    }
]

MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'middleware.http.Http403Middleware',
    'reversion.middleware.RevisionMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'oidc_provider.middleware.SessionManagementMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # this is default
    'guardian.backends.ObjectPermissionBackend',
    'oauth2_provider.backends.OAuth2Backend',
)

ROOT_URLCONF = 'onlineweb4.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'onlineweb4.wsgi.application'

INSTALLED_APPS = (
    # Third party dependencies
    'django.contrib.humanize',
    'django_js_reverse',
    'django_nose',
    'django_nyt', # Wiki
    'mptt', # Wiki
    'sekizai', # Wiki
    'sorl.thumbnail', # Wiki
    'chunks',
    'crispy_forms',
    'django_extensions',
    'django_dynamic_fixture',
    'oauth2_provider',
    'captcha',
    'rest_framework_recaptcha',
    'pdfdocument',
    'watson',
    'markdown_deux',
    'reversion',
    'guardian',
    'stripe',
    'rest_framework',
    'django_filters',
    'taggit',
    'taggit_serializer',
    'corsheaders',
    'datetimewidget',
    'webpack_loader',
    'oidc_provider',
    'raven.contrib.django.raven_compat',  # Sentry, error tracking

    # Django apps
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    # Onlineweb 4 apps
    'apps.api',
    'apps.approval',
    'apps.article',
    'apps.authentication',
    'apps.autoconfig',
    'apps.careeropportunity',
    'apps.companyprofile',
    'apps.contact',
    'apps.contribution',
    'apps.dashboard',
    'apps.dataporten',
    'apps.gallery',
    'apps.gsuite',
    'apps.hobbygroups',
    'apps.events',
    'apps.marks',
    'apps.offline',
    'apps.feedback',
    'apps.mommy',
    'apps.profiles',
    'apps.resourcecenter',
    'apps.mailinglists',
    'apps.inventory',
    'apps.payment',
    'apps.posters',
    #'apps.rutinator',
    'apps.slack',
    'apps.sso',
    'apps.splash',
    'apps.shop',
    'apps.webshop',
    'apps.chunksapi',
    'scripts',

    #External apps
    'redwine',

    #Wiki
    'wiki',
    'wiki.plugins.attachments',
    'wiki.plugins.images',
    'wiki.plugins.macros',
    'wiki.plugins.help',
    'wiki.plugins.links',
    'wiki.plugins.globalhistory',
)

# Make Django messages use bootstrap alert classes
MESSAGE_TAGS = {messages.DEBUG: 'alert-debug',
                messages.INFO: 'alert-info',
                messages.SUCCESS: 'alert-success',
                messages.WARNING: 'alert-warning',
                messages.ERROR: 'alert-danger'}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    }
]
