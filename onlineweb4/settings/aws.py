import os
from .base import PROJECT_ROOT_DIRECTORY
from .django import MEDIA_ROOT, STATIC_ROOT
from decouple import config

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config("OW4_DB_NAME", default="postgres"),
        "USER": config("OW4_DB_USERNAME", default="postgres"),
        "PASSWORD": config("OW4_DB_PASSWORD", default="postgres"),
        "HOST": config("OW4_DB_HOST", default="localhost"),
        "PORT": config("OW4_DB_PORT", default="5432"),
        "CONN_MAX_AGE": None,
    }
}

EMAIL_FILE_PATH = config("OW4_MAIL_LOG_PATH", default="/srv/app/logs/mail.log")

GOOGLE_ANALYTICS_KEY = config("OW4_GOOGLE_ANALYTICS_KEY", default="")

# Filebrowser local settings.
FILEBROWSER_MEDIA_ROOT = MEDIA_ROOT

RFID_API_KEY = config("OW4_RFID_API_KEY", default="")

# Generalforsamling admin password
GENFORS_ADMIN_PASSWORD = config("OW4_GENFORS_ADMIN_PASSWORD", default="")


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("OW4_CACHE_LOCATION", default="redis://localhost:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        }
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
JANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True


WIKI_ATTACHMENTS_EXTENSIONS = [
    "pdf",
    "doc",
    "odt",
    "docx",
    "txt",
    "xlsx",
    "xls",
    "png",
    "psd",
    "ai",
    "ods",
    "zip",
    "jpg",
    "jpeg",
    "gif",
    "patch",
]

WIKI_MARKDOWN_HTML_WHITELIST = ["br", "hr"]


BEDKOM_GROUP_ID = config("OW4_BEDKOM_GROUP_ID", cast=int, default=0)
FAGKOM_GROUP_ID = config("OW4_FAGKOM_GROUP_ID", cast=int, default=0)
COMMON_GROUP_ID = config("OW4_COMMON_GROUP_ID", cast=int, default=0)

SYMPA_DB_PASSWD = config("OW4_SYMPA_DB_PASSWORD", default="")
SYMPA_DB_USER = config("OW4_SYMPA_DB_USERNAME", default="")
SYMPA_DB_NAME = config("OW4_SYMPA_DB_NAME", default="")
SYMPA_DB_PORT = config("OW4_SYMPA_DB_PORT", cast=int, default=5432)
SYMPA_DB_HOST = config("OW4_SYMPA_DB_HOST", default="")


# TEMPORARY FIX DURING DJANGO GUARDIAN DEBUGGING
ANONYMOUS_USER_ID = config("OW4_ANONYMOUS_USER_ID", cast=int, default=0)

SLACK_INVITER = {"team_name": "onlinentnu", "token": config("OW4_SLACK_INVITER_TOKEN", default="")}

APPROVAL_SETTINGS = {"SEND_APPROVER_NOTIFICATION_EMAIL": False}

OW4_USE_S3 = config("OW4_USE_AWS_S3", cast=bool, default=False)
OW4_USE_CLOUDFRONT = config("OW4_USE_CLOUDFRONT", cast=bool, default=False)

if OW4_USE_S3:
    AWS_ACCESS_KEY_ID = config("OW4_AWS_ACCESS_KEY")
    AWS_SECRET_ACCESS_KEY = config("OW4_AWS_SECRET_KEY")
    AWS_STORAGE_BUCKET_NAME = config("OW4_AWS_S3_BUCKET")
    AWS_S3_REGION_NAME = config("OW4_AWS_REGION")

    AWS_IS_GZIPPED = True
    AWS_QUERYSTRING_AUTH = False
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

    OW4_S3_PREFIX = config("OW4_AWS_S3_PREFIX", default="")

    STATICFILES_STORAGE = "onlineweb4.storage_backends.AWSS3StaticStorage"
    DEFAULT_FILE_STORAGE = "onlineweb4.storage_backends.AWSS3PublicMediaStorage"
    WIKI_STORAGE_BACKEND = "onlineweb4.storage_backends.AWSS3WikiStorage"

    if OW4_USE_CLOUDFRONT:
        AWS_S3_CUSTOM_DOMAIN = config("OW4_AWS_CLOUDFRONT_DOMAIN")

    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_ROOT}/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_ROOT}/"
