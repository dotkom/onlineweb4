from django.conf.urls import url
from django.urls import path
from oauth2_provider.views.base import TokenView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.settings import api_settings
from apps.api import views as api_views
from apps.shop import views as shop_views

schema_view = get_schema_view(
    openapi.Info(
        title="Onlineweb4 API",
        default_version='1.0.0',
        description="Rest API for Onlineweb4 backend",
    ),
    public=True,
    authentication_classes=api_settings.DEFAULT_AUTHENTICATION_CLASSES,
    permission_classes=api_settings.DEFAULT_PERMISSION_CLASSES,
)

urlpatterns = [
    url(r"^v1/rfid/$", shop_views.SetRFIDView.as_view(), name="set_rfid"),
    url(r"^v1/auth/$", TokenView.as_view(), name="oauth2_provider_token"),
    path("v1/docs/", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^v1/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(
        "v1/openapi-schema",
        api_views.OpenAPISchemaView.as_view(),
        name="openapi",
    ),
]
