from decouple import config

S3_MEDIA_STORAGE_ENABLED = config("OW4_USE_S3", cast=bool, default=False)
if S3_MEDIA_STORAGE_ENABLED:
    AWS_S3_REGION_NAME = config("OW4_S3_REGION", default="eu-north-1")
    AWS_STORAGE_BUCKET_NAME = config("OW4_S3_BUCKET_NAME")
    AWS_S3_CUSTOM_DOMAIN = (
        f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
    )
    AWS_S3_ENDPOINT_URL = f"https://s3.{AWS_S3_REGION_NAME}.amazonaws.com"
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_DEFAULT_ACL = "public-read"
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }

    MEDIA_LOCATION = "media"

    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/"
    MEDIA_ROOT = ""

    STATIC_LOCATION = "static"

    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/"

    WIKI_ATTACHMENTS_LOCAL_PATH = False
    WIKI_ATTACHMENTS_APPEND_EXTENSION = False

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "location": MEDIA_LOCATION,
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "location": STATIC_LOCATION,
            },
        },
    }
