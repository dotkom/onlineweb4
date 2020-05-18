from django.views.generic import TemplateView
from rest_framework.schemas import openapi
from rest_framework.schemas.views import SchemaView
from rest_framework.settings import api_settings


class SwaggerUIView(TemplateView):
    template_name = "api/swagger-ui.html"
    extra_context = {"schema_url": "openapi-schema"}


class OpenAPISchemaView(SchemaView):
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES
    schema_generator = openapi.SchemaGenerator(
        title="Onlineweb4 API",
        description="Rest API for Onlineweb4 backend",
        version="1.0.0",
    )
    public = False
