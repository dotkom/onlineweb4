# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.urls import path

from apps.api import views as api_views
from apps.shop import views as shop_views
from apps.sso import views as sso_views

urlpatterns = [
    url(r"^v1/rfid/$", shop_views.SetRFIDView.as_view(), name="set_rfid"),
    url(r"^v1/auth/$", sso_views.TokenView.as_view(), name="oauth2_provider_token"),
    path("v1/docs/", api_views.SwaggerUIView.as_view(), name="swagger-ui"),
    path(
        "v1/openapi-schema",
        api_views.OpenAPISchemaView.as_view(),
        name="openapi-schema",
    ),
]
