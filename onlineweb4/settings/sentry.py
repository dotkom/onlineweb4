import sentry_sdk
from decouple import config
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from sentry_sdk.integrations.django import DjangoIntegration

OW4_SENTRY_DSN = config("OW4_SENTRY_DSN", default="")


sentry_sdk.init(
    dsn=OW4_SENTRY_DSN,
    environment=config("OW4_ENVIRONMENT", default="DEVELOP"),
    traces_sample_rate=0.2,
    integrations=[DjangoIntegration(), AwsLambdaIntegration(timeout_warning=True)],
)
