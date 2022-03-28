from decouple import config

from .django import DEBUG

OW4_SENTRY_DSN = config("OW4_SENTRY_DSN", default="")

if OW4_SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=OW4_SENTRY_DSN,
        environment=config("OW4_ENVIRONMENT", default="DEVELOP"),
        debug=DEBUG,
        release=config("OW4_RELEASE"),
        traces_sample_rate=0.2,
        integrations=[DjangoIntegration(), AwsLambdaIntegration(timeout_warning=True)],
    )
