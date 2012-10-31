import os
import sys

PROJECT_SETTINGS_DIRECTORY = os.path.dirname(globals()['__file__'])
PROJECT_ROOT_DIRECTORY = os.path.join(PROJECT_SETTINGS_DIRECTORY, '../..')

TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
NOSE_ARGS = ['--with-coverage', '--cover-package=apps']

DEBUG = False
TEMPLATE_DEBUG = DEBUG

TEST_RUNNER = "django_nose.NoseTestSuiteRunner"

ADMINS = (
    ('dotKom', 'dotkom@online.ntnu.no'),
)
MANAGERS = ADMINS

# Email settings
DEFAULT_FROM_EMAIL = 'online@online.ntnu.no'
EMAIL_ARRKOM = 'arrkom@online.ntnu.no'
EMAIL_BEDKOM = 'bedkom@online.ntnu.no'
EMAIL_DOTKOM = 'dotkom@online.ntnu.no'
EMAIL_FAGKOM = 'fagkom@online.ntnu.no'
EMAIL_PROKOM = 'prokom@online.ntnu.no'
EMAIL_TRIKOM = 'trikom@online.ntnu.no'

TIME_ZONE = 'Europe/Oslo'
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'nb'
LANGUAGES = (
                ('nb', 'Norwegian'),
                ('en_US', 'English'),
            )

SITE_ID = 1
USE_I18N = True
USE_L10N = True
DATETIME_FORMAT = 'N j, Y, H:i'

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True
SECRET_KEY = 'q#wy0df(7&amp;$ucfrxa1j72%do7ko*-6(g!8f$tc2$3x@3cq5@6c'

AUTH_PROFILE_MODULE = 'apps.userprofile.UserProfile'

MEDIA_ROOT = '/some/absolute/path/in/prod/'
UPLOAD_DIRECTORY = 'uploads/'

if DEBUG:
    MEDIA_ROOT = 'media/'

STATIC_ROOT = 'static/'
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT_DIRECTORY, 'static/'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'onlineweb4.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'onlineweb4.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT_DIRECTORY, 'templates/')
)

FILEBROWSER_DIRECTORY = "" # becomes MEDIA_ROOT

INSTALLED_APPS = (
    # Third party dependencies
    'django_nose',
    'south',
    'grappelli',
    'filebrowser',

    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    # Onlineweb 4 apps
    'apps.article',
    'apps.autoconfig',
    'apps.events',
    'apps.userprofile',
)

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
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

for settings_module in ['local', ]:
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
        exec('from %s import *' % settings_module)
    except ImportError, e:
        print "Could not import settings for '%s' : %s" % (settings_module,
                str(e))
