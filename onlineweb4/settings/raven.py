import os
import raven

from decouple import config

from .base import PROJECT_ROOT_DIRECTORY

RAVEN_CONFIG = {
    'dsn': config('OW4_RAVEN_DSN', default=''),  # Format: https://user:pass@sentry.io/project
    'environment': config('OW4_ENVIRONMENT', default='DEVELOP'),
    # Use git to determine release
    'release': raven.fetch_git_sha(PROJECT_ROOT_DIRECTORY),
    'tags': { 'app': config('OW4_RAVEN_APP_NAME', default='') },
}
