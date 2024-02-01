# Django REST framework
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "apps.api.utils.PrefixRemovedAutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # Allows user to be logged in with open-id
        "apps.online_oidc_provider.authentication.OidcOauth2Auth",
        # allow accesssing API with JWT from our Authorization Server
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # Allows users to be logged in to browsable API
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FileUploadParser",
    ),
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework.renderers.AdminRenderer",
    ],
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_METADATA_CLASS": "utils.metadata.ActionMeta",
    "DEFAULT_PAGINATION_CLASS": "utils.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}
