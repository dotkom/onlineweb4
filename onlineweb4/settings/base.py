import os
import sys
from django.contrib.messages import constants as messages

# Directory that contains this file.
PROJECT_SETTINGS_DIRECTORY = os.path.dirname(globals()['__file__'])
# Root directory. Contains manage.py
PROJECT_ROOT_DIRECTORY = os.path.join(PROJECT_SETTINGS_DIRECTORY, '..', '..')
#PROJECT_ROOT_DIRECTORY = os.path.dirname(os.path.dirname(__file__))

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
USE_TZ = False
DATETIME_FORMAT = 'N j, Y, H:i'
SECRET_KEY = 'q#wy0df(7&amp;$ucfrxa1j72%do7ko*-6(g!8f$tc2$3x@3cq5@6c'

AUTH_USER_MODEL = 'authentication.OnlineUser'
LOGIN_URL = '/auth/login/'

MEDIA_ROOT = os.path.join(PROJECT_ROOT_DIRECTORY, 'uploaded_media') # Override this in local.py in prod.
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_ROOT_DIRECTORY, 'static')
STATIC_URL = '/static/'

#Url of default profile picture
DEFAULT_PROFILE_PICTURE_URL = os.path.join(STATIC_URL, "img", "profile_default.png")

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT_DIRECTORY, 'files/static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_OUTPUT_DIR = 'cache'
COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} {outfile}'),
)

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor-filters.cssmin.CSSMinFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc -x {infile} {outfile}'),
)

# List of callables that know how to import templates from various sources.
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
    'middleware.http.Http403Middleware',
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
GRAPPELLI_ADMIN_TITLE = '<a href="/">Onlineweb</a>'

INSTALLED_APPS = (
    # Third party dependencies
    'django.contrib.humanize',
    'django_nose',
    'south',
    'django_notify',
    'mptt',
    'sekizai',
    'sorl.thumbnail',
    'grappelli',
    'filebrowser',
    'chunks',
    'crispy_forms',
    'django_extensions',
    'django_dynamic_fixture',
    'captcha',
    'compressor',
    'watson',
    'django_ldapbackend',

    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.markup',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    # Onlineweb 4 apps
    'apps.article',
    'apps.authentication',
    'apps.autoconfig',
    'apps.careeropportunity',
    'apps.companyprofile',
    'apps.events',
    'apps.marks',
    'apps.offline',
    'apps.feedback',
    'apps.mommy',
    'apps.profiles',
    
    # Wiki-related stuff
    'wiki',
    'wiki.plugins.attachments',
    'wiki.plugins.notifications',
    'wiki.plugins.images',
    'wiki.plugins.macros',    
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
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'apscheduler.scheduler': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}

# crispy forms settings
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# bootstrap messages classes
MESSAGE_TAGS = {messages.DEBUG: 'alert-debug',
                messages.INFO: 'alert-info',
                messages.SUCCESS: 'alert-success',
                messages.WARNING: 'alert-warning',
                messages.ERROR: 'alert-error'}


# Not really sure what this does.
# Has something to do with django-dynamic-fixture bumped from 1.6.4 to 1.6.5 in order to run a syncdb with mysql/postgres (OptimusCrime)
IMPORT_DDF_MODELS = False

# Required by the Wiki
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "sekizai.context_processors.sekizai",
)

# Remember to keep 'local' last, so it can override any setting.
for settings_module in ['filebrowser', 'local']:  # local last
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
