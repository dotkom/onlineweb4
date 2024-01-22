from .base import PROJECT_ROOT_DIRECTORY

LOG_DIR = PROJECT_ROOT_DIRECTORY / "log"

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}
    },
    "handlers": {
        "null": {"level": "DEBUG", "class": "logging.NullHandler"},
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "django.security.DisallowedHost": {"handlers": ["null"], "propagate": False},
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "feedback": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "syncer": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "": {"handlers": ["console"], "level": "DEBUG", "propagate": True},
    },
}
