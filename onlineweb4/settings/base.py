import os
import sys

from decouple import config

from apps.sso.settings import OAUTH2_SCOPES

# Directory that contains this file.
PROJECT_SETTINGS_DIRECTORY = os.path.dirname(globals()['__file__'])
# Root directory. Contains manage.py
PROJECT_ROOT_DIRECTORY = os.path.join(PROJECT_SETTINGS_DIRECTORY, '..', '..')

sys.dont_write_bytecode = config("OW4_PYTHON_DONT_WRITE_BYTECODE", cast=bool, default=True)

# OW4 settings

APPROVAL_SETTINGS = {
    'SEND_APPLICANT_NOTIFICATION_EMAIL': True,
    'SEND_APPROVER_NOTIFICATION_EMAIL': True,
    'SEND_COMMITTEEAPPLICATION_APPLICANT_EMAIL': config('OW4_APPROVAL_SEND_COMMITTEEAPPLICATION_APPLICANT_EMAIL',
                                                        default=False, cast=bool),
}

OW4_SETTINGS = {
   'events': {
       'ENABLE_RECAPTCHA': config('OW4_EVENTS_ENABLE_RECAPTCHA', True, cast=bool),
       'FEATURED_DAYS_FUTURE': os.getenv('OW4_EVENTS_FEATURED_DAYS_FUTURE', 3),
       'FEATURED_DAYS_PAST': os.getenv('OW4_EVENTS_FEATURED_DAYS_PAST', 3),
   }
}

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
    'oidc_provider',

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
    'apps.gsuite',
    'apps.hobbygroups',
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
    'apps.photoalbum',
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
    'team_name': config("OW4_DJANGO_SLACK_INVITER_TEAM_NAME", default='team_name_here'),
    # Token generated using OAuth2: https://api.slack.com/docs/oauth
    # Scopes needed: client+admin
    'token': config("OW4_DJANGO_SLACK_INVITER_TOKEN", default='xoxp-1234_fake'),
}

# SSO / OAuth2 settings
OAUTH2_PROVIDER = {
    'SCOPES': OAUTH2_SCOPES,
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600,
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 60,
}
OAUTH2_PROVIDER_APPLICATION_MODEL = 'sso.Client'

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'webpack/',  # end with slash
        'STATS_FILE': os.path.join(
            PROJECT_ROOT_DIRECTORY,
            config('OW4_WEBPACK_LOADER_STATS_FILE', default='webpack-stats.json')
        )
    }
}


# Third party application settings

# Django Guardian settings
ANONYMOUS_USER_NAME = 'anonymoususer'
GUARDIAN_RENDER_403 = True


# Django-Taggit settings
TAGGIT_CASE_INSENSITIVE = True

# crispy forms settings
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Not really sure what this does.
# Has something to do with django-dynamic-fixture bumped from 1.6.4 to 1.6.5 in order to run a syncdb with mysql/postgres (OptimusCrime)
IMPORT_DDF_MODELS = False

# Django CORS headers
CORS_ORIGIN_ALLOW_ALL = config("OW4_DJANGO_CORS_ORIGIN_ALLOW_ALL", cast=bool, default=True)
CORS_URLS_REGEX = r'^(/api/v1/.*|/sso/user/|/openid/.*)$' # Enables CORS on all /api/v1/, /sso/user/ and all /openid/ endpoints


# Google reCaptcha settings
# Keys are found here: https://online.ntnu.no/wiki/komiteer/dotkom/aktuelt/onlineweb4/keys/
RECAPTCHA_PUBLIC_KEY = config("OW4_DJANGO_RECAPTCHA_PUBLIC_KEY", default='6LfV9jkUAAAAANqYIOgveJ0pOowXvNCcsYzRi7Y_')
RECAPTCHA_PRIVATE_KEY = config("OW4_DJANGO_RECAPTCHA_PRIVATE_KEY", default='6LfV9jkUAAAAABlc4-q01vMsBNv3-Gsp75G8Zd5N')
NOCAPTCHA = config("OW4_DJANGO_NOCAPTCHA", cast=bool, default=True)
RECAPTCHA_USE_SSL = config("OW4_DJANGO_RECAPTCHA_USE_SSL", cast=bool, default=True)


# oidc_provider - OpenID Connect Provider
OIDC_USERINFO = 'apps.online_oidc_provider.claims.userinfo'
OIDC_EXTRA_SCOPE_CLAIMS = 'apps.online_oidc_provider.claims.Onlineweb4ScopeClaims'

USE_X_FORWARDED_HOST = config("OW4_DJANGO_DEVELOPMENT_HTTPS", cast=bool, default=False)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') if USE_X_FORWARDED_HOST else None

VIMEO_API_TOKEN = config('OW4_VIMEO_API_TOKEN', default=None)
