from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object


class OIDCAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "mozilla_django_oidc.contrib.drf.OIDCAuthentication"
    name = "jwtAuth"

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name="HTTP_AUTHORIZATION",
            token_prefix="Bearer ",
            bearer_format="JWT",
        )
