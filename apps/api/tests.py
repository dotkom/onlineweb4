from django.urls import reverse
from rest_framework import status

from apps.online_oidc_provider.test import OIDCTestCase


class OpenAPISchemaTestCase(OIDCTestCase):
    """
    Test schema generation for different permissions on user.
    Different permissions will generate different schemas, since you can only see
    schemas for endpoints you have permission to access.
    """

    def setUp(self):
        super().setUp()
        self.url = reverse("openapi-schema")

    def test_can_generate_schema_as_anonymous(self):
        response = self.client.get(self.url, **self.bare_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_generate_schema_as_regular_user(self):
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_generate_schema_as_super_user(self):
        self.user.is_superuser = True
        self.user.save()
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SwaggerUITestCase(OIDCTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("swagger-ui")

    def test_can_generate_schema_as_anonymous(self):
        response = self.client.get(self.url, **self.bare_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_generate_schema_as_regular_user(self):
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
