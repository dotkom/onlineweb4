# -*- coding: utf8 -*-
import os
import sys

import wiki
from django.contrib.messages import constants as messages

# Directory that contains this file.
PROJECT_SETTINGS_DIRECTORY = os.path.dirname(globals()['__file__'])
# Root directory. Contains manage.py
PROJECT_ROOT_DIRECTORY = os.path.join(PROJECT_SETTINGS_DIRECTORY, '..', '..')

TEST_RUNNER = "django_nose.NoseTestSuiteRunner"

NOSE_ARGS = ['--with-coverage', '--cover-package=apps', '--cover-html-dir=coverage', '--cover-xml', '--cover-html']

DEBUG = False

ADMINS = (
    ('dotKom', 'dotkom@online.ntnu.no'),
)
MANAGERS = ADMINS

# Email settings
DEFAULT_FROM_EMAIL = 'online@online.ntnu.no'
EMAIL_ARRKOM = 'arrkom@online.ntnu.no'
EMAIL_BEDKOM = 'bedkom@online.ntnu.no'
EMAIL_DOTKOM = 'dotkom@online.ntnu.no'
EMAIL_EKSKOM = 'ekskom@online.ntnu.no'
EMAIL_FAGKOM = 'fagkom@online.ntnu.no'
EMAIL_HS = 'hs@online.ntnu.no'
EMAIL_ITEX = 'itex@online.ntnu.no'
EMAIL_PROKOM = 'prokom@online.ntnu.no'
EMAIL_TRIKOM = 'trikom@online.ntnu.no'

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
SECRET_KEY = 'override-this-in-local.py'

# Session cookie expires after one year
SESSION_COOKIE_AGE = 31540000

# Override this in local if you need to :)
BASE_URL = 'https://online.ntnu.no'

AUTH_USER_MODEL = 'authentication.OnlineUser'
LOGIN_URL = '/auth/login/'

MEDIA_ROOT = os.path.join(PROJECT_ROOT_DIRECTORY, 'uploaded_media')  # Override this in local.py in prod.
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_ROOT_DIRECTORY, 'static')
STATIC_URL = '/static/'

# Prefix for default profile picture
DEFAULT_PROFILE_PICTURE_PREFIX = os.path.join(STATIC_URL, "img", "profile_default")

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT_DIRECTORY, 'files/static'),
    os.path.join(PROJECT_ROOT_DIRECTORY, 'assets'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

# Including django-wiki static files so we can import the less files.
DJANGO_WIKI_STATIC = os.path.join(os.path.dirname(wiki.__file__), 'static')

COMPRESS_FILES = True
COMPRESS_OUTPUT_DIR = 'cache'
COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc --include-path=%s {infile} {outfile}' % DJANGO_WIKI_STATIC),
)

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    # We want this later on, but it breaks production so disabling for now.
    #'compressor-filters.cssmin.CSSMinFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

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
                "onlineweb4.context_processors.analytics",
            ],
            'debug': DEBUG,
        }
    }
]

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'middleware.http.Http403Middleware',
    'reversion.middleware.RevisionMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # this is default
    'guardian.backends.ObjectPermissionBackend',
)

ROOT_URLCONF = 'onlineweb4.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'onlineweb4.wsgi.application'

# Pizzasystem settings
PIZZA_GROUP = 'dotkom'
PIZZA_ADMIN_GROUP = 'pizzaadmin'

# Grappelli settings
GRAPPELLI_ADMIN_TITLE = 'Onlineweb'

# Guardian settings
ANONYMOUS_USER_NAME = 'anonymoususer'
GUARDIAN_RENDER_403 = True

# Django-Taggit settings
TAGGIT_CASE_INSENSITIVE = True

# List of usergroups that should be listed under "Finn brukere" in user profile
USER_SEARCH_GROUPS = [
    16,  # appKom
    1,   # arrKom
    2,   # banKom
    3,   # bedKom
    4,   # dotKom
    5,   # eksKom
    14,  # Eldsteradet
    6,   # fagKom
    11,  # Hovedstyret
    19,  # jubKom
    10,  # pangKom
    7,   # proKom
    18,  # seniorKom
    8,   # triKom
    9,   # velKom
    24,  # itex
]

#List of mailing lists, used in update_sympa_memcache_from_sql.py
PUBLIC_LISTS = [
    "foreninger",
    "linjeforeninger",
    "gloshaugen",
    "dragvoll",
    "masterforeninger",
    "kjellere",
    "linjeledere",
    "linjeredaksjoner",
    "glosfaddere",
    "sr-samarbeid",
    "ivt-samarbeid",
    "linjekor",
    "studentdemokratiet"
]

INSTALLED_APPS = (
    # Third party dependencies
    'django.contrib.humanize',
    'django_nose',
    'django_nyt', # Wiki
    'mptt', # Wiki
    'sekizai', # Wiki
    'sorl.thumbnail', # Wiki
    'grappelli',
    'filebrowser',
    'chunks',
    'crispy_forms',
    'django_extensions',
    'django_dynamic_fixture',
    'oauth2_provider',
    'captcha',
    'compressor',
    'pdfdocument',
    'watson',
    'markdown_deux',
    'djangoformsetjs',
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

    # Django apps
    'django.contrib.admin',
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
    'apps.dashboard',
    'apps.gallery',
    'apps.events',
    'apps.marks',
    'apps.offline',
    'apps.feedback',
    'apps.mommy',
    'apps.profiles',
    'apps.genfors',
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
    'scripts',

    #External apps
    'feedme',
    'redwine',

    #Wiki
    'wiki',
    'wiki.plugins.attachments',
    'wiki.plugins.images',
    'wiki.plugins.macros',
    'wiki.plugins.help',
    'wiki.plugins.links',

)


# SSO / OAuth2 settings
if 'apps.sso' in INSTALLED_APPS:
    from apps.sso.settings import OAUTH2_SCOPES
    OAUTH2_PROVIDER = {
        'SCOPES': OAUTH2_SCOPES,
        'ACCESS_TOKEN_EXPIRE_SECONDS': 3600,
        'AUTHORIZATION_CODE_EXPIRE_SECONDS': 60,
    }
    OAUTH2_PROVIDER_APPLICATION_MODEL = 'sso.Client'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'feedback': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'syncer': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

SLACK_INVITER = {
    # e.g. onlinentnu
    'team_name': 'team_name_here',
    # Token generated using OAuth2: https://api.slack.com/docs/oauth
    # Scopes needed: client+admin
    'token': 'xoxp-1234_fake'
}

# crispy forms settings
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# bootstrap messages classes
MESSAGE_TAGS = {messages.DEBUG: 'alert-debug',
                messages.INFO: 'alert-info',
                messages.SUCCESS: 'alert-success',
                messages.WARNING: 'alert-warning',
                messages.ERROR: 'alert-danger'}


# Not really sure what this does.
# Has something to do with django-dynamic-fixture bumped from 1.6.4 to 1.6.5 in order to run a syncdb with mysql/postgres (OptimusCrime)
IMPORT_DDF_MODELS = False

# Django REST framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',  # Allows users to be logged in to browsable API
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FileUploadParser',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.AdminRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/v1/.*$' # Enables CORS on /api/v1/ endpoints only

OW4_SETTINGS = {
   'events': {
       'FEATURED_DAYS_FUTURE': os.getenv('OW4_EVENTS_FEATURED_DAYS_FUTURE', 3),
       'FEATURED_DAYS_PAST': os.getenv('OW4_EVENTS_FEATURED_DAYS_PAST', 3),
   }
}

APPROVAL_SETTINGS = {
    'SEND_APPROVER_NOTIFICATION_EMAIL': True,
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    }
]

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'webpack_bundles/'  # end with slash
    }
}

# Remember to keep 'local' last, so it can override any setting.
for settings_module in ['filebrowser', 'django_wiki', 'local']:  # local last
    if not os.path.exists(os.path.join(PROJECT_SETTINGS_DIRECTORY,
            settings_module + ".py")):
        sys.stderr.write("Could not find settings module '%s'.\n" %
                settings_module)
        if settings_module == 'local':
            sys.stderr.write("You need to copy the settings file "
                             "'onlineweb4/settings/example-local.py' to "
                             "'onlineweb4/settings/local.py'.\n")
        sys.exit(1)
    try:
        exec('from .%s import *' % settings_module)
    except ImportError as e:
        print("Could not import settings for '%s' : %s" % (settings_module,
                str(e)))
