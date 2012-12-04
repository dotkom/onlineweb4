import os
import sys

# Directory that contains this file.
PROJECT_SETTINGS_DIRECTORY = os.path.dirname(globals()['__file__'])
# Root directory. Contains manage.py
PROJECT_ROOT_DIRECTORY = os.path.join(PROJECT_SETTINGS_DIRECTORY, '../..')

TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
NOSE_ARGS = ['--with-coverage', '--cover-package=apps']

DEBUG = False
TEMPLATE_DEBUG = DEBUG

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

# We will receive errors and other django messages from this email
SERVER_EMAIL = 'onlineweb4-error@online.ntnu.no'

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
USE_TZ = False
SECRET_KEY = 'q#wy0df(7&amp;$ucfrxa1j72%do7ko*-6(g!8f$tc2$3x@3cq5@6c'

AUTH_PROFILE_MODULE = 'userprofile.UserProfile'

MEDIA_ROOT = os.path.join(PROJECT_ROOT_DIRECTORY, 'media') # Override this in local.py in prod.
MEDIA_URL = '/media/'

STATIC_ROOT = 'static/'
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

# Grappelli settings
GRAPPELLI_ADMIN_TITLE = 'Onlineweb'

INSTALLED_APPS = (
    # Third party apps
    'south',
    'django_nose',
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

    # Onlineweb apps
    'apps.events',
    'apps.userprofile',
    'apps.authentication',
    'apps.autoconfig'
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

for settings_module in ['filebrowser', 'local', ]: # Remember to keep 'local' last, so it can override any setting.
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
