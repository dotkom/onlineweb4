from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.test import APITestCase


class OpenAPISchemaTestCase(APITestCase):
    """
    Test schema generation for different permissions on user.
    Different permissions will generate different schemas, since you can only see
    schemas for endpoints you have permission to access.
    """

    def setUp(self):
        super().setUp()
        self.url = reverse("openapi-schema")
        self.user = G("authentication.OnlineUser")
        self.client.force_authenticate(user=self.user)

    def test_can_generate_schema_as_anonymous(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_generate_schema_as_regular_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_generate_schema_as_super_user(self):
        self.user.is_superuser = True
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SwaggerUITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("swagger-ui")
        self.user = G("authentication.OnlineUser")

    def test_can_generate_schema_as_anonymous(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_generate_schema_as_regular_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
