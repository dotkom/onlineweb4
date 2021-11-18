import os

from decouple import config

from .base import PROJECT_ROOT_DIRECTORY

LOG_DIR = os.path.join(PROJECT_ROOT_DIRECTORY, "log")
