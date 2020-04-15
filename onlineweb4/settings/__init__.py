import sys


from onlineweb4.settings.django import *
from onlineweb4.settings.base import *
from onlineweb4.settings.celery import *
from onlineweb4.settings.dataporten import *
from onlineweb4.settings.django_wiki import *
from onlineweb4.settings.gsuite import *
from onlineweb4.settings.logging import *
from onlineweb4.settings.raven import *
from onlineweb4.settings.rest_framework import *
from onlineweb4.settings.stripe import *

try:
    from onlineweb4.settings.local import *
except ImportError as e:
    pass

if config("OW4_ENVIRONMENT", default="") == "AWS_PROD" or config("OW4_ENVIRONMENT", default="") == "AWS_DEV" :
    from onlineweb4.settings.aws import *
