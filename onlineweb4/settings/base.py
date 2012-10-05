import os
import sys

PROJECT_ROOT_DIRECTORY = os.path.join(os.path.dirname(globals()['__file__']),'../..')
PROJECT_SETTINGS_DIRECTORY = os.path.join(PROJECT_ROOT_DIRECTORY, 'onlineweb4', 'settings')

TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
NOSE_ARGS = ['--with-coverage', '--cover-package=apps']

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('dotKom', 'dotkom@online.ntnu.no'),
)

MANAGERS = ADMINS


TIME_ZONE = 'Europe/Oslo'
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'nb'

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
SECRET_KEY = 'q#wy0df(7&amp;$ucfrxa1j72%do7ko*-6(g!8f$tc2$3x@3cq5@6c'


AUTH_PROFILE_MODULE = 'apps.userprofile.UserProfile'


# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT_DIRECTORY, 'static/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
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

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_nose',
    'django_assets',
    'south',
    'apps.events',
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

for settings_module in ['local',]:
    if not os.path.exists(os.path.join(PROJECT_SETTINGS_DIRECTORY, settings_module + ".py")):
        sys.stderr.write("Could not find settings module '%s'. Project settings path: %s", settings_module, PROJECT_SETTINGS_DIRECTORY)
        if settings_module == 'local':
            print "You need to copy the settings file 'onlineweb4/settings/example-local.py' to 'onlineweb4/settings/local.py'."
        sys.exit(1)
    try:
        exec('from %s import *' % settings_module)
    except ImportError, e:
        print "Could not import settings for '%s' : %s" % (settings_module, str(e))
