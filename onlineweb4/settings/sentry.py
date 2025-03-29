import sentry_sdk
from decouple import config
from rest_framework.serializers import ValidationError
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from sentry_sdk.integrations.django import DjangoIntegration

OW4_SENTRY_DSN = config("OW4_SENTRY_DSN", default="")


sentry_sdk.init(
    dsn=OW4_SENTRY_DSN,
    environment=config("OW4_ENVIRONMENT", default="DEVELOP"),
    traces_sample_rate=1.0,
    profiles_sample_rate=0.2,
    integrations=[DjangoIntegration(), AwsLambdaIntegration(timeout_warning=True)],
    ignore_errors=[ValidationError],
)


def sentry_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        sentry_sdk.set_user(
            None if request.user.is_anonymous else {"id": request.user.pk}
        )
        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware
