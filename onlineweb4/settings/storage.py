from decouple import config

S3_MEDIA_STORAGE_ENABLED = config("OW4_USE_S3", cast=bool, default=False)
if S3_MEDIA_STORAGE_ENABLED:
    from storages.backends.s3boto3 import S3Boto3Storage

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

    class MediaRootS3BotoStorage(S3Boto3Storage):
        def __init__(self, **kwargs):
            super().__init__(**(kwargs | {"location": MEDIA_LOCATION}))

    DEFAULT_FILE_STORAGE = "onlineweb4.settings.MediaRootS3BotoStorage"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/"
    MEDIA_ROOT = ""

    STATIC_LOCATION = "static"

    class StaticRootS3BotoStorage(S3Boto3Storage):
        def __init__(self, **kwargs):
            super().__init__(**(kwargs | {"location": STATIC_LOCATION}))

    STATICFILES_STORAGE = "onlineweb4.settings.StaticRootS3BotoStorage"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/"

    WIKI_ATTACHMENTS_LOCAL_PATH = False
    WIKI_ATTACHMENTS_APPEND_EXTENSION = False
