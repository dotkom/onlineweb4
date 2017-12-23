import sys


from onlineweb4.settings.base import *
from onlineweb4.settings.django_wiki import *
from onlineweb4.settings.filebrowser import *
from onlineweb4.settings.raven import *

try:
    from onlineweb4.settings.local import *
except ImportError as e:
    # No local settings file found.
    # You can still override using environment variables.
    pass
