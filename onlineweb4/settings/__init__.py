from decouple import config

from onlineweb4.settings.base import *
from onlineweb4.settings.dataporten import *
from onlineweb4.settings.django import *
from onlineweb4.settings.django_wiki import *
from onlineweb4.settings.gsuite import *
from onlineweb4.settings.logging import *
from onlineweb4.settings.rest_framework import *
from onlineweb4.settings.sentry import *
from onlineweb4.settings.storage import *
from onlineweb4.settings.stripe import *
from onlineweb4.settings.vapid import *

try:
    from onlineweb4.settings.local import *
except ImportError:
    # No local settings file found.
    # You can still override using environment variables.
    pass
try:
    if config("OW4_ZAPPA", cast=bool, default=False):
        from onlineweb4.settings.zappa import *
except ImportError:
    pass
