import os
import raven

from decouple import config

RAVEN_CONFIG = {
    'dsn': config('OW4_RAVEN_DSN', default=''),  # Format: https://user:pass@sentry.io/project
    'environment': config('OW4_ENVIRONMENT', default='DEVELOP'),
    # Use git to determine release
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
    'tags': { 'app': config('OW4_RAVEN_APP_NAME', default='') },
}
