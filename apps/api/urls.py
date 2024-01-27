from django.urls import path

from apps.api import views as api_views

urlpatterns = [
    path("v1/docs/", api_views.SwaggerUIView.as_view(), name="swagger-ui"),
    path(
        "v1/openapi-schema",
        api_views.OpenAPISchemaView.as_view(),
        name="openapi-schema",
    ),
]
