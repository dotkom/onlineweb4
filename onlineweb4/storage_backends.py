from storages.backends.s3boto3 import S3Boto3Storage
from onlineweb4.settings.aws import OW4_S3_PREFIX
from django.conf import settings


class AWSS3StaticStorage(S3Boto3Storage):
    location = OW4_S3_PREFIX + "/static"

class AWSS3PrivateStorage(S3Boto3Storage):
    location = OW4_S3_PREFIX + "/private"

class AWSS3PublicMediaStorage(S3Boto3Storage):
    location = OW4_S3_PREFIX + "/media"
    file_overwrite = False

class AWSS3WikiStorage(S3Boto3Storage):
    location = OW4_S3_PREFIX + "/wiki"
    file_overwrite = False
