from decouple import config

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration


OW4_SENTRY_DSN = config("OW4_SENTRY_DSN", default="")

sentry_sdk.init(
    dsn=OW4_SENTRY_DSN,
    environment=config("OW4_ENVIRONMENT", default="DEVELOP"),
    debug=config("OW4_DJANGO_DEBUG", cast=bool, default="False"),
    traces_sample_rate=0.2,
    integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
)
