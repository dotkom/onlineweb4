from django.urls import path, re_path
from oauth2_provider.views.base import TokenView

from apps.api import views as api_views
from apps.shop import views as shop_views

urlpatterns = [
    re_path(r"^v1/rfid/$", shop_views.SetRFIDView.as_view(), name="set_rfid"),
    re_path(r"^v1/auth/$", TokenView.as_view(), name="oauth2_provider_token"),
    path("v1/docs/", api_views.SwaggerUIView.as_view(), name="swagger-ui"),
    path(
        "v1/openapi-schema",
        api_views.OpenAPISchemaView.as_view(),
        name="openapi-schema",
    ),
]
